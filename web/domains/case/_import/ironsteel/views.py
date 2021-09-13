from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.db.models import Sum
from django.forms.models import model_to_dict
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from storages.backends.s3boto3 import S3Boto3StorageFile

from web.domains.case.app_checks import get_org_update_request_errors
from web.domains.case.forms import DocumentForm, SubmitForm
from web.domains.case.utils import (
    check_application_permission,
    get_application_current_task,
    view_application_file,
)
from web.domains.file.utils import create_file_model
from web.domains.template.models import Template
from web.flow.models import Task
from web.types import AuthenticatedHttpRequest
from web.utils.commodity import get_category_commodity_group_data
from web.utils.validation import (
    ApplicationErrors,
    FieldError,
    PageErrors,
    create_page_errors,
)

from .. import views as import_views
from .forms import (
    AddCertificateForm,
    EditCertificateForm,
    EditIronSteelForm,
    IronSteelChecklistForm,
    IronSteelChecklistOptionalForm,
    ResponsePrepCertificateForm,
    ResponsePrepGoodsForm,
)
from .models import IronSteelApplication, IronSteelChecklist


@login_required
def edit_ironsteel(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        task = get_application_current_task(application, "import", Task.TaskType.PREPARE)

        if request.POST:
            form = EditIronSteelForm(data=request.POST, instance=application)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk})
                )

        else:
            form = EditIronSteelForm(instance=application, initial={"contact": request.user})

        supporting_documents = application.supporting_documents.filter(is_active=True)
        certificates = application.certificates.filter(is_active=True)

        category_commodity_groups = get_category_commodity_group_data(commodity_type="IRON_STEEL")

        if application.category_commodity_group:
            selected_group = category_commodity_groups.get(
                application.category_commodity_group.pk, {}
            )
        else:
            selected_group = {}

        context = {
            "process_template": "web/domains/case/import/partials/process.html",
            "process": application,
            "task": task,
            "form": form,
            "page_title": "Iron and Steel (Quota) Import Licence - Edit",
            "supporting_documents": supporting_documents,
            "category_commodity_groups": category_commodity_groups,
            "commodity_group_label": selected_group.get("label", ""),
            "certificates": certificates,
            "case_type": "import",
        }

        return render(request, "web/domains/case/import/ironsteel/edit.html", context)


@login_required
def submit_ironsteel(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        task = get_application_current_task(application, "import", Task.TaskType.PREPARE)

        errors = ApplicationErrors()

        edit_errors = PageErrors(
            page_name="Application details",
            url=reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk}),
        )
        create_page_errors(
            EditIronSteelForm(data=model_to_dict(application), instance=application), edit_errors
        )
        errors.add(edit_errors)

        certificates = application.certificates.filter(is_active=True)

        if not certificates.exists():
            certificate_errors = PageErrors(
                page_name="Add Certificates",
                url=reverse(
                    "import:ironsteel:add-certificate", kwargs={"application_pk": application_pk}
                ),
            )

            certificate_errors.add(
                FieldError(
                    "Certificates",
                    messages=["At least one certificate must be added."],
                )
            )

            errors.add(certificate_errors)

        elif application.quantity:
            total_certificates = certificates.aggregate(sum_requested=Sum("requested_qty")).get(
                "sum_requested"
            )
            if total_certificates != application.quantity:
                for cert in certificates:
                    certificate_errors = PageErrors(
                        page_name=f"Edit Certificate: {cert.reference}",
                        url=reverse(
                            "import:ironsteel:edit-certificate",
                            kwargs={"application_pk": application_pk, "document_pk": cert.pk},
                        ),
                    )

                    certificate_errors.add(
                        FieldError(
                            f"Requested Quantity: {cert.requested_qty} kg (imported goods {application.quantity} kg)",
                            messages=[
                                (
                                    "Please ensure that the sum of export certificate requested"
                                    " quantities equals the total quantity of imported goods."
                                )
                            ],
                        )
                    )

                    errors.add(certificate_errors)

        errors.add(get_org_update_request_errors(application, "import"))

        if request.POST:
            form = SubmitForm(data=request.POST)

            if form.is_valid() and not errors.has_errors():
                application.submit_application(request, task)

                # TODO: replace with Endorsement Usage Template (ICMSLST-638)
                # endorsements are active on ICMS1 but inactive in our db
                # endorsement = Template.objects.get(
                #     is_active=True,
                #     template_type=Template.ENDORSEMENT,
                #     template_name="Endorsement 1 (must be updated each year)",
                # )
                # application.endorsements.create(content=endorsement.template_content)

                return application.redirect_after_submit(request)

        else:
            form = SubmitForm()

        declaration = Template.objects.filter(
            is_active=True,
            template_type=Template.DECLARATION,
            application_domain=Template.IMPORT_APPLICATION,
            template_code="IMA_GEN_DECLARATION",
        ).first()

        context = {
            "process_template": "web/domains/case/import/partials/process.html",
            "process": application,
            "task": task,
            "form": form,
            "page_title": "Iron and Steel (Quota) Import Licence - Submit",
            "declaration": declaration,
            "errors": errors if errors.has_errors() else None,
            "case_type": "import",
        }

        return render(request, "web/domains/case/import/ironsteel/submit.html", context)


@login_required
def add_document(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        task = get_application_current_task(application, "import", Task.TaskType.PREPARE)

        if request.POST:
            form = DocumentForm(data=request.POST, files=request.FILES)

            if form.is_valid():
                document = form.cleaned_data.get("document")
                create_file_model(document, request.user, application.supporting_documents)

                return redirect(
                    reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk})
                )
        else:
            form = DocumentForm()

        context = {
            "process_template": "web/domains/case/import/partials/process.html",
            "process": application,
            "task": task,
            "form": form,
            "page_title": "Iron and Steel (Quota) Import Licence - Add supporting document",
            "case_type": "import",
        }

        return render(
            request, "web/domains/case/import/ironsteel/add_supporting_document.html", context
        )


@require_GET
@login_required
def view_document(
    request: AuthenticatedHttpRequest, *, application_pk: int, document_pk: int
) -> HttpResponse:
    application: IronSteelApplication = get_object_or_404(IronSteelApplication, pk=application_pk)

    return view_application_file(
        request.user, application, application.supporting_documents, document_pk, "import"
    )


@require_POST
@login_required
def delete_document(
    request: AuthenticatedHttpRequest, *, application_pk: int, document_pk: int
) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        get_application_current_task(application, "import", Task.TaskType.PREPARE)

        document = application.supporting_documents.get(pk=document_pk)
        document.is_active = False
        document.save()

        return redirect(reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk}))


@login_required
def add_certificate(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        task = get_application_current_task(application, "import", Task.TaskType.PREPARE)

        if request.POST:
            form = AddCertificateForm(data=request.POST, files=request.FILES)

            if form.is_valid():
                document: S3Boto3StorageFile = form.cleaned_data.get("document")

                extra_args = {
                    field: value
                    for (field, value) in form.cleaned_data.items()
                    if field not in ["document"]
                }

                create_file_model(
                    document,
                    request.user,
                    application.certificates,
                    extra_args=extra_args,
                )

                return redirect(
                    reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk})
                )
        else:
            form = AddCertificateForm()

        context = {
            "process_template": "web/domains/case/import/partials/process.html",
            "process": application,
            "task": task,
            "form": form,
            "page_title": "Iron and Steel (Quota) Import Licence - Add certificate",
            "case_type": "import",
        }

        return render(request, "web/domains/case/import/ironsteel/add_certificate.html", context)


@require_GET
@login_required
def view_certificate(
    request: AuthenticatedHttpRequest, *, application_pk: int, document_pk: int
) -> HttpResponse:
    application = get_object_or_404(IronSteelApplication, pk=application_pk)

    return import_views.view_file(request, application, application.certificates, document_pk)


@require_POST
@login_required
def delete_certificate(
    request: AuthenticatedHttpRequest, *, application_pk: int, document_pk: int
) -> HttpResponse:
    with transaction.atomic():
        application = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        get_application_current_task(application, "import", Task.TaskType.PREPARE)

        document = application.certificates.get(pk=document_pk)
        document.is_active = False
        document.save()

        return redirect(reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk}))


@login_required
def edit_certificate(
    request: AuthenticatedHttpRequest, *, application_pk: int, document_pk: int
) -> HttpResponse:
    with transaction.atomic():
        application = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, "import")

        task = get_application_current_task(application, "import", Task.TaskType.PREPARE)

        document = application.certificates.get(pk=document_pk)

        if request.POST:
            form = EditCertificateForm(data=request.POST, instance=document)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse("import:ironsteel:edit", kwargs={"application_pk": application_pk})
                )

        else:
            form = EditCertificateForm(instance=document)

        context = {
            "process_template": "web/domains/case/import/partials/process.html",
            "process": application,
            "task": task,
            "form": form,
            "page_title": "Iron and Steel (Quota) Import Licence - Edit certificate",
            "case_type": "import",
        }

        return render(request, "web/domains/case/import/ironsteel/edit_certificate.html", context)


@login_required
@permission_required("web.reference_data_access", raise_exception=True)
def manage_checklist(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )
        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)
        checklist, created = IronSteelChecklist.objects.get_or_create(
            import_application=application
        )

        if request.POST:
            form = IronSteelChecklistOptionalForm(request.POST, instance=checklist)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "import:ironsteel:manage-checklist",
                        kwargs={"application_pk": application_pk},
                    )
                )
        else:
            if created:
                form = IronSteelChecklistForm(instance=checklist)
            else:
                form = IronSteelChecklistForm(data=model_to_dict(checklist), instance=checklist)

        context = {
            "process": application,
            "task": task,
            "page_title": "Iron and Steel (Quota) Import Licence - Checklist",
            "form": form,
        }

        return render(
            request=request,
            template_name="web/domains/case/import/management/checklist.html",
            context=context,
        )


@login_required
@permission_required("web.reference_data_access", raise_exception=True)
def response_preparation_edit_goods(
    request: AuthenticatedHttpRequest, *, application_pk: int
) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)

        if request.POST:
            form = ResponsePrepGoodsForm(data=request.POST, instance=application)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "case:prepare-response",
                        kwargs={"application_pk": application_pk, "case_type": "import"},
                    )
                )

        else:
            form = ResponsePrepGoodsForm(instance=application)

        context = {
            "process": application,
            "task": task,
            "form": form,
            "case_type": "import",
            "page_title": "Iron and Steel (Quota) Import Licence - Edit Goods",
        }

        return render(
            request, "web/domains/case/import/manage/response-prep-edit-form.html", context
        )


@login_required
@permission_required("web.reference_data_access", raise_exception=True)
def response_preparation_edit_certificate(
    request: AuthenticatedHttpRequest,
    *,
    application_pk: int,
    document_pk: int,
) -> HttpResponse:
    with transaction.atomic():
        application: IronSteelApplication = get_object_or_404(
            IronSteelApplication.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)

        document = application.certificates.get(pk=document_pk)

        if request.POST:
            form = ResponsePrepCertificateForm(data=request.POST, instance=document)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "case:prepare-response",
                        kwargs={"application_pk": application_pk, "case_type": "import"},
                    )
                )

        else:
            form = ResponsePrepCertificateForm(instance=document)

        context = {
            "process": application,
            "task": task,
            "form": form,
            "case_type": "import",
            "page_title": "Iron and Steel (Quota) Import Licence - Edit Certificate",
        }

        return render(
            request, "web/domains/case/import/manage/response-prep-edit-form.html", context
        )
