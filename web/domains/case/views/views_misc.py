from typing import TYPE_CHECKING, Any, Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import ObjectDoesNotExist
from django.http import Http404, HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView, View
from guardian.shortcuts import get_users_with_perms

from web.domains.case import forms
from web.domains.case.app_checks import get_app_errors
from web.domains.case.models import DocumentPackBase, VariationRequest
from web.domains.case.services import case_progress, document_pack
from web.domains.case.shared import ImpExpStatus
from web.domains.case.tasks import create_case_document_pack
from web.domains.case.types import ImpOrExp
from web.domains.case.utils import (
    check_application_permission,
    end_process_task,
    get_application_current_task,
    get_case_page_title,
)
from web.domains.template.models import Template
from web.domains.user.models import User
from web.flow import errors
from web.flow.models import Task
from web.models import WithdrawApplication
from web.notify.email import send_email
from web.types import AuthenticatedHttpRequest
from web.utils.s3 import delete_file_from_s3, get_s3_client
from web.utils.validation import ApplicationErrors

from .mixins import ApplicationAndTaskRelatedObjectMixin, ApplicationTaskMixin
from .utils import get_class_imp_or_exp, get_current_task_and_readonly_status

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from web.domains.case.types import DocumentPack


# "Applicant Case Management" Views
@login_required
@require_POST
def cancel_case(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    with transaction.atomic():
        model_class = get_class_imp_or_exp(case_type)
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, case_type)

        # TODO: Check this - Can you cancel a case that is in a variation request etc.
        try:
            case_progress.check_expected_status(application, [ImpExpStatus.IN_PROGRESS])
            case_progress.check_expected_task(application, Task.TaskType.PREPARE)
        except errors.ProcessError:
            raise PermissionDenied

        application.delete()

        messages.success(request, "Application has been cancelled.")

        return redirect(reverse("workbasket"))


@login_required
def withdraw_case(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    with transaction.atomic():
        model_class = get_class_imp_or_exp(case_type)
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, case_type)
        application.check_expected_status(
            [ImpExpStatus.SUBMITTED, ImpExpStatus.PROCESSING, ImpExpStatus.VARIATION_REQUESTED]
        )

        if request.method == "POST":
            form = forms.WithdrawForm(request.POST)

            if form.is_valid():
                withdrawal = form.save(commit=False)

                if case_type == "import":
                    withdrawal.import_application = application
                elif case_type == "export":
                    withdrawal.export_application = application

                withdrawal.status = WithdrawApplication.STATUS_OPEN
                withdrawal.request_by = request.user
                withdrawal.save()

                application.update_order_datetime()
                application.save()

                messages.success(
                    request,
                    "You have requested that this application be withdrawn. Your request has been sent to ILB.",
                )

                return redirect(reverse("workbasket"))
        else:
            form = forms.WithdrawForm()

        context = {
            "process": application,
            "page_title": get_case_page_title(case_type, application, "Withdrawals"),
            "form": form,
            "withdrawals": application.withdrawals.filter(is_active=True),
            "case_type": case_type,
        }
        return render(request, "web/domains/case/withdraw.html", context)


@login_required
@require_POST
def archive_withdrawal(
    request: AuthenticatedHttpRequest, *, application_pk: int, withdrawal_pk: int, case_type: str
) -> HttpResponse:
    with transaction.atomic():
        model_class = get_class_imp_or_exp(case_type)
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, case_type)
        application.check_expected_status(
            [ImpExpStatus.SUBMITTED, ImpExpStatus.PROCESSING, ImpExpStatus.VARIATION_REQUESTED]
        )

        withdrawal = get_object_or_404(application.withdrawals, pk=withdrawal_pk)
        withdrawal.is_active = False
        withdrawal.save()

        messages.success(
            request, "You have retracted your request for this application to be withdrawn."
        )

        return redirect(reverse("workbasket"))


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def manage_withdrawals(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        task, readonly_view = get_current_task_and_readonly_status(
            application, case_type, request.user, Task.TaskType.PROCESS
        )

        withdrawals = application.withdrawals.filter(is_active=True).order_by("-created_datetime")
        current_withdrawal = withdrawals.filter(status=WithdrawApplication.STATUS_OPEN).first()

        if request.method == "POST" and not readonly_view:
            form = forms.WithdrawResponseForm(request.POST, instance=current_withdrawal)

            if form.is_valid():
                withdrawal = form.save(commit=False)
                withdrawal.response_by = request.user
                withdrawal.save()

                # withdrawal accepted - case is closed, else case still open
                if withdrawal.status == WithdrawApplication.STATUS_ACCEPTED:
                    if application.status == ImpExpStatus.VARIATION_REQUESTED:
                        application.status = ImpExpStatus.COMPLETED
                        # Close the open variation request if we are withdrawing the application / variation
                        vr = application.variation_requests.get(status=VariationRequest.OPEN)
                        vr.status = VariationRequest.WITHDRAWN
                        vr.reject_cancellation_reason = application.variation_refuse_reason
                        vr.closed_datetime = timezone.now()
                        vr.save()
                    else:
                        application.status = model_class.Statuses.WITHDRAWN
                        application.is_active = False

                    application.update_order_datetime()
                    application.save()

                    end_process_task(task, request.user)

                    return redirect(reverse("workbasket"))
                else:
                    end_process_task(task)

                    Task.objects.create(
                        process=application, task_type=Task.TaskType.PROCESS, previous=task
                    )

                    return redirect(
                        reverse(
                            "case:manage-withdrawals",
                            kwargs={"application_pk": application_pk, "case_type": case_type},
                        )
                    )
        else:
            form = forms.WithdrawResponseForm(instance=current_withdrawal)

        context = {
            "process": application,
            "page_title": get_case_page_title(case_type, application, "Withdrawals"),
            "form": form,
            "withdrawals": withdrawals,
            "current_withdrawal": current_withdrawal,
            "case_type": case_type,
            "readonly_view": readonly_view,
        }

        return render(
            request=request,
            template_name="web/domains/case/manage/withdrawals.html",
            context=context,
        )


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
@require_POST
def take_ownership(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        application.get_task(
            expected_state=[
                model_class.Statuses.SUBMITTED,
                model_class.Statuses.VARIATION_REQUESTED,
            ],
            task_type=Task.TaskType.PROCESS,
        )

        if application.status == model_class.Statuses.SUBMITTED:
            application.status = model_class.Statuses.PROCESSING

            if case_type == "import":
                # Licence start date is set when ILB Admin takes the case
                licence = document_pack.pack_draft_get(application)

                if not licence.licence_start_date:
                    licence.licence_start_date = timezone.now().date()
                    licence.save()

            # TODO: Revisit when implementing ICMSLST-1169
            # We may need to create some more datetime fields

        application.case_owner = request.user
        application.update_order_datetime()
        application.save()

        return redirect(
            reverse(
                "case:manage", kwargs={"application_pk": application.pk, "case_type": case_type}
            )
        )


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
@require_POST
def release_ownership(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        get_application_current_task(application, case_type, Task.TaskType.PROCESS)

        if application.status != model_class.Statuses.VARIATION_REQUESTED:
            application.status = model_class.Statuses.SUBMITTED

        application.case_owner = None
        application.update_order_datetime()
        application.save()

        return redirect(reverse("workbasket"))


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def manage_case(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        task, readonly_view = get_current_task_and_readonly_status(
            application, case_type, request.user, Task.TaskType.PROCESS
        )

        if request.method == "POST" and not readonly_view:
            form = forms.CloseCaseForm(request.POST)

            if form.is_valid():
                application.status = model_class.Statuses.STOPPED
                application.save()

                end_process_task(task)

                if form.cleaned_data.get("send_email"):
                    template = Template.objects.get(template_code="STOP_CASE")

                    subject = template.get_title({"CASE_REFERENCE": application.pk})
                    body = template.get_content({"CASE_REFERENCE": application.pk})

                    if case_type == "import":
                        users = get_users_with_perms(
                            application.importer, only_with_perms_in=["is_contact_of_importer"]
                        ).filter(user_permissions__codename="importer_access")
                    else:
                        users = get_users_with_perms(
                            application.exporter, only_with_perms_in=["is_contact_of_exporter"]
                        ).filter(user_permissions__codename="exporter_access")

                    recipients = set(users.values_list("email", flat=True))

                    send_email(subject, body, recipients)

                messages.success(
                    request,
                    "This case has been stopped and removed from your workbasket."
                    " It will still be available from the search screen.",
                )

                return redirect(reverse("workbasket"))
        else:
            form = forms.CloseCaseForm()

        context = {
            "case_type": case_type,
            "process": application,
            "page_title": get_case_page_title(case_type, application, "Manage"),
            "form": form,
            "readonly_view": readonly_view,
        }

        return render(
            request=request, template_name="web/domains/case/manage/manage.html", context=context
        )


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def start_authorisation(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    """Authorise the application, in legacy this is called "Close Case Processing".

    `application.decision` is used to determine the next steps.
    """

    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, case_type, Task.TaskType.PROCESS)

        application_errors: ApplicationErrors = get_app_errors(application, case_type)

        if request.method == "POST" and not application_errors.has_errors():
            create_documents = True

            if application.status == application.Statuses.VARIATION_REQUESTED:
                if (
                    application.is_import_application()
                    and application.variation_decision == application.REFUSE
                ):
                    vr = application.variation_requests.get(status=VariationRequest.OPEN)
                    next_task = None
                    application.status = model_class.Statuses.COMPLETED
                    vr.status = VariationRequest.REJECTED
                    vr.reject_cancellation_reason = application.variation_refuse_reason
                    vr.closed_datetime = timezone.now()

                    vr.save()

                    create_documents = False
                else:
                    next_task = Task.TaskType.AUTHORISE

            else:
                if application.decision == application.REFUSE:
                    next_task = Task.TaskType.REJECTED
                    application.status = model_class.Statuses.COMPLETED
                    create_documents = False

                else:
                    next_task = Task.TaskType.AUTHORISE
                    application.status = model_class.Statuses.PROCESSING

            application.update_order_datetime()
            application.save()

            end_process_task(task)

            if next_task:
                Task.objects.create(process=application, task_type=next_task, previous=task)

            if create_documents:
                document_pack.doc_ref_documents_create(application, request.icms.lock_manager)
            else:
                document_pack.pack_draft_archive(application)

            return redirect(reverse("workbasket"))

        else:
            context = {
                "case_type": case_type,
                "process": application,
                "page_title": get_case_page_title(case_type, application, "Authorisation"),
                "errors": application_errors if application_errors.has_errors() else None,
            }

            return render(
                request=request,
                template_name="web/domains/case/authorisation.html",
                context=context,
            )


@login_required
@sensitive_post_parameters("password")
@permission_required("web.ilb_admin", raise_exception=True)
def authorise_documents(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, case_type, Task.TaskType.AUTHORISE)

        if request.method == "POST":
            form = forms.AuthoriseForm(data=request.POST, request=request)

            if form.is_valid():
                end_process_task(task, request.user)
                Task.objects.create(
                    process=application, task_type=Task.TaskType.DOCUMENT_SIGNING, previous=task
                )

                application.update_order_datetime()
                application.save()

                # Queues all documents to be created
                create_case_document_pack(application, request.user)

                messages.success(
                    request,
                    f"Authorise Success: Application {application.reference} has been queued for document signing",
                )

                return redirect(reverse("workbasket"))

        else:
            form = forms.AuthoriseForm(request=request)

        context = {
            "case_type": case_type,
            "process": application,
            "page_title": get_case_page_title(case_type, application, "Authorisation"),
            "form": form,
            "primary_recipients": _get_primary_recipients(application),
            "copy_recipients": _get_copy_recipients(application),
        }

        return render(
            request=request,
            template_name="web/domains/case/authorise-documents.html",
            context=context,
        )


class CheckCaseDocumentGenerationView(
    ApplicationTaskMixin, PermissionRequiredMixin, LoginRequiredMixin, View
):
    # View Config
    http_method_names = ["get"]

    # ApplicationTaskMixin Config
    current_status = [
        ImpExpStatus.PROCESSING,
        ImpExpStatus.VARIATION_REQUESTED,
        ImpExpStatus.COMPLETED,
    ]

    # PermissionRequiredMixin Config
    permission_required = ["web.ilb_admin"]

    def get(self, request: HttpRequest, *args, **kwargs) -> Any:
        self.set_application_and_task()

        active_tasks = self.application.get_active_task_list()

        reload_workbasket = False

        if (
            self.application.status == ImpExpStatus.COMPLETED
            or Task.TaskType.CHIEF_WAIT in active_tasks
        ):
            msg = "Documents generated successfully"
            reload_workbasket = True

        elif Task.TaskType.DOCUMENT_ERROR in active_tasks:
            msg = "Failed to generate documents"
            reload_workbasket = True

        elif Task.TaskType.DOCUMENT_SIGNING in active_tasks:
            msg = "Documents are still being generated"

        elif Task.TaskType.CHIEF_ERROR in active_tasks:
            msg = "Unable to send licence details to HMRC"
            reload_workbasket = True

        else:
            # TODO: Sent a sentry message instead to handle the error gracefully
            raise Exception("Unknown state for application")

        return JsonResponse(data={"msg": msg, "reload_workbasket": reload_workbasket})


@method_decorator(transaction.atomic, name="post")
class RecreateCaseDocumentsView(
    ApplicationTaskMixin, PermissionRequiredMixin, LoginRequiredMixin, View
):
    # View Config
    http_method_names = ["post"]

    # ApplicationTaskMixin Config
    current_status = [ImpExpStatus.PROCESSING, ImpExpStatus.VARIATION_REQUESTED]
    current_task_type = Task.TaskType.DOCUMENT_ERROR
    next_task_type = Task.TaskType.DOCUMENT_SIGNING

    # PermissionRequiredMixin Config
    permission_required = ["web.ilb_admin"]

    def post(self, request: HttpRequest, *args, **kwargs) -> Any:
        """Deletes existing draft PDFs and regenerates case document pack"""
        self.set_application_and_task()
        doc_pack = document_pack.pack_draft_get(self.application)
        documents = document_pack.doc_ref_documents_all(doc_pack)

        s3_client = get_s3_client()
        for cdr in documents:
            if cdr.document and cdr.document.path:
                delete_file_from_s3(cdr.document.path, s3_client)

        self.update_application_tasks()
        create_case_document_pack(self.application, self.request.user)

        self.application.update_order_datetime()
        self.application.save()

        messages.success(
            request,
            f"Recreate Case Documents Success:"
            f" Application {self.application.reference} has been queued for document signing",
        )

        return redirect(reverse("workbasket"))


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def view_document_packs(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    """ILB Admin view to view the application documents before authorising."""

    with transaction.atomic():
        model_class = get_class_imp_or_exp(case_type)
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        get_application_current_task(application, case_type, Task.TaskType.AUTHORISE)

        context = {
            "case_type": case_type,
            "process": application,
            "page_title": get_case_page_title(case_type, application, "Authorisation"),
            "primary_recipients": _get_primary_recipients(application),
            "copy_recipients": _get_copy_recipients(application),
            **get_document_context(application),
        }

        return render(
            request=request,
            template_name="web/domains/case/document-packs.html",
            context=context,
        )


def get_document_context(
    application: ImpOrExp,
    issued_document: Optional["DocumentPack"] = None,
) -> dict[str, str]:
    at = application.application_type

    if application.is_import_application():
        # A supplied document pack or the current draft pack
        licence = issued_document or document_pack.pack_draft_get(application)

        licence_doc = document_pack.doc_ref_licence_get(licence)
        cover_letter = document_pack.doc_ref_cover_letter_get(licence)

        # If issued_document is not None then we are viewing completed documents
        if application.status == ImpExpStatus.COMPLETED or issued_document:
            licence_url = reverse(
                "case:view-case-document",
                kwargs={
                    "application_pk": application.id,
                    "case_type": "import",
                    "object_pk": licence.pk,
                    "casedocumentreference_pk": licence_doc.pk,
                },
            )
            cover_letter_url = reverse(
                "case:view-case-document",
                kwargs={
                    "application_pk": application.id,
                    "case_type": "import",
                    "object_pk": licence.pk,
                    "casedocumentreference_pk": cover_letter.pk,
                },
            )
        else:
            licence_url = reverse(
                "case:licence-pre-sign",
                kwargs={"application_pk": application.pk, "case_type": "import"},
            )
            cover_letter_url = reverse(
                "case:preview-cover-letter",
                kwargs={"application_pk": application.pk, "case_type": "import"},
            )

        context = {
            "cover_letter_flag": at.cover_letter_flag,
            "type_label": at.Types(at.type).label,
            "customs_copy": at.type == at.Types.OPT,
            "is_cfs": False,
            "document_reference": licence_doc.reference,
            "licence_url": licence_url,
            "cover_letter_url": cover_letter_url,
        }
    else:
        # A supplied document pack or the current draft pack
        certificate = issued_document or document_pack.pack_draft_get(application)

        certificate_docs = document_pack.doc_ref_certificates_all(certificate)
        document_reference = ", ".join(c.reference for c in certificate_docs)

        context = {
            "cover_letter_flag": False,
            "type_label": at.type,
            "customs_copy": False,
            "is_cfs": at.type_code == at.Types.FREE_SALE,
            "document_reference": document_reference,
            # TODO: Revisit when we can generate an export certificate
            # https://uktrade.atlassian.net/browse/ICMSLST-1406
            # https://uktrade.atlassian.net/browse/ICMSLST-1407
            # https://uktrade.atlassian.net/browse/ICMSLST-1408
            "certificate_links": [],
        }

    return context


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
@require_POST
def cancel_authorisation(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, case_type, Task.TaskType.AUTHORISE)

        if application.status != model_class.Statuses.VARIATION_REQUESTED:
            application.status = model_class.Statuses.PROCESSING

        application.update_order_datetime()
        application.save()

        end_process_task(task, request.user)

        Task.objects.create(process=application, task_type=Task.TaskType.PROCESS, previous=task)

        return redirect(reverse("workbasket"))


class ViewIssuedCaseDocumentsView(
    ApplicationTaskMixin, PermissionRequiredMixin, LoginRequiredMixin, TemplateView
):
    # ApplicationTaskMixin Config
    current_status = [ImpExpStatus.COMPLETED]

    # TemplateView Config
    http_method_names = ["get"]
    template_name = "web/domains/case/view-case-documents.html"

    def has_permission(self):
        application = self.get_object().get_specific_model()

        try:
            check_application_permission(application, self.request.user, self.kwargs["case_type"])
        except PermissionDenied:
            return False

        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        application = self.application
        is_import_app = application.is_import_application()

        case_type = self.kwargs["case_type"]
        context["page_title"] = get_case_page_title(case_type, application, "Issued Documents")
        context["process"] = self.application
        context["primary_recipients"] = _get_primary_recipients(application)
        context["copy_recipients"] = _get_copy_recipients(application)
        context["case_type"] = case_type
        context["org"] = application.importer if is_import_app else application.exporter

        issued_documents = document_pack.pack_issued_get_all(self.application)

        issued_doc = issued_documents.get(pk=self.kwargs["issued_document_pk"])
        context["issue_date"] = issued_doc.case_completion_datetime

        return context | get_document_context(self.application, issued_doc)


@method_decorator(transaction.atomic, name="post")
class ClearIssuedCaseDocumentsFromWorkbasket(
    ApplicationAndTaskRelatedObjectMixin, PermissionRequiredMixin, LoginRequiredMixin, View
):
    # ApplicationAndTaskRelatedObjectMixin Config
    current_status = [ImpExpStatus.COMPLETED]

    # View Config
    http_method_names = ["post"]

    def has_permission(self):
        self.set_application_and_task()

        try:
            check_application_permission(
                self.application, self.request.user, self.kwargs["case_type"]
            )
        except PermissionDenied:
            return False

        return True

    def post(self, request: HttpRequest, *args, **kwargs) -> Any:
        """Remove the document pack from the workbasket."""
        pack_pk = self.kwargs["issued_document_pk"]

        try:
            document_pack.pack_workbasket_remove_pack(self.application, pack_pk=pack_pk)
        except ObjectDoesNotExist:
            raise Http404("No %s matches the given query." % DocumentPackBase._meta.object_name)

        self.update_application_tasks()

        return redirect(reverse("workbasket"))


def _get_primary_recipients(application: ImpOrExp) -> "QuerySet[User]":
    if application.agent:
        return application.get_agent_contacts()
    else:
        return application.get_org_contacts()


def _get_copy_recipients(application: ImpOrExp) -> "QuerySet[User]":
    if application.agent:
        return application.get_org_contacts()
    else:
        return User.objects.none()
