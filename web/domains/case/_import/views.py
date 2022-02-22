from typing import TYPE_CHECKING, Any, List, Type

import django.forms as django_forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.exceptions import PermissionDenied
from django.db import models, transaction
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import DetailView, ListView, TemplateView
from guardian.shortcuts import get_objects_for_user

from web.domains.case.models import VariationRequest
from web.domains.case.utils import (
    create_acknowledge_notification_task,
    get_application_current_task,
)
from web.domains.country.models import CountryGroup
from web.domains.importer.models import Importer
from web.domains.user.models import User
from web.flow.models import ProcessTypes, Task
from web.types import AuthenticatedHttpRequest
from web.utils.s3 import get_file_from_s3

from .derogations.models import DerogationsApplication
from .fa_dfl.models import DFLApplication
from .fa_oil.models import OpenIndividualLicenceApplication
from .fa_sil.models import SILApplication
from .forms import (
    CoverLetterForm,
    CreateImportApplicationForm,
    CreateWoodQuotaApplicationForm,
    EndorsementChoiceImportApplicationForm,
    EndorsementImportApplicationForm,
    LicenceDateAndPaperLicenceForm,
    LicenceDateForm,
    OPTLicenceForm,
)
from .ironsteel.models import IronSteelApplication
from .models import (
    ImportApplication,
    ImportApplicationLicence,
    ImportApplicationType,
    get_paper_licence_only,
)
from .opt.models import OutwardProcessingTradeApplication
from .sanctions.models import SanctionsAndAdhocApplication
from .sps.models import PriorSurveillanceApplication
from .textiles.models import TextilesApplication
from .wood.models import WoodQuotaApplication

if TYPE_CHECKING:
    from django.db.models import QuerySet


def _get_disabled_application_types() -> dict[str, bool]:
    return {
        "show_opt": ImportApplicationType.objects.get(
            type=ImportApplicationType.Types.OPT
        ).is_active,
        "show_textiles": ImportApplicationType.objects.get(
            type=ImportApplicationType.Types.TEXTILES
        ).is_active,
        "show_sps": ImportApplicationType.objects.get(
            type=ImportApplicationType.Types.SPS
        ).is_active,
        "show_ironsteel": ImportApplicationType.objects.get(
            type=ImportApplicationType.Types.IRON_STEEL
        ).is_active,
    }


class ImportApplicationChoiceView(PermissionRequiredMixin, TemplateView):
    template_name = "web/domains/case/import/choose.html"
    permission_required = "web.importer_access"

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        context.update(**_get_disabled_application_types())

        return context


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_derogations(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.DEROGATION,  # type: ignore[arg-type]
        model_class=DerogationsApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_sanctions(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.SANCTION_ADHOC,  # type: ignore[arg-type]
        model_class=SanctionsAndAdhocApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_firearms_oil(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.FIREARMS,  # type: ignore[arg-type]
        application_subtype=ImportApplicationType.SubTypes.OIL,  # type: ignore[arg-type]
        model_class=OpenIndividualLicenceApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_firearms_dfl(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.FIREARMS,  # type: ignore[arg-type]
        application_subtype=ImportApplicationType.SubTypes.DFL,  # type: ignore[arg-type]
        model_class=DFLApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_firearms_sil(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.FIREARMS,  # type: ignore[arg-type]
        application_subtype=ImportApplicationType.SubTypes.SIL,  # type: ignore[arg-type]
        model_class=SILApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_wood_quota(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.WOOD_QUOTA,  # type: ignore[arg-type]
        model_class=WoodQuotaApplication,
        form_class=CreateWoodQuotaApplicationForm,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_opt(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.OPT,  # type: ignore[arg-type]
        model_class=OutwardProcessingTradeApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_textiles(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.TEXTILES,  # type: ignore[arg-type]
        model_class=TextilesApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_sps(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.SPS,  # type: ignore[arg-type]
        model_class=PriorSurveillanceApplication,
    )


@login_required
@permission_required("web.importer_access", raise_exception=True)
def create_ironsteel(request: AuthenticatedHttpRequest) -> HttpResponse:
    return _create_application(
        request,
        application_type=ImportApplicationType.Types.IRON_STEEL,  # type: ignore[arg-type]
        model_class=IronSteelApplication,
    )


def _importers_with_agents(user: User) -> List[int]:
    importers_with_agents = get_objects_for_user(user, ["web.is_agent_of_importer"], Importer)
    return [importer.pk for importer in importers_with_agents]


def _create_application(
    request: AuthenticatedHttpRequest,
    *,
    application_type: ImportApplicationType.Types,
    application_subtype: ImportApplicationType.SubTypes = None,
    model_class: Type[ImportApplication],
    form_class: Type[CreateImportApplicationForm] = None,
) -> HttpResponse:
    """Helper function to create one of several types of importer application.

    :param request: Django request
    :param import_application_type: ImportApplicationType type or sub_type
    :param model_class: ImportApplication class
    :param form_class: Optional form class that defines extra logic
    :return:
    """

    qs = ImportApplicationType.objects.filter(type=application_type)

    if application_subtype:
        qs = qs.filter(sub_type=application_subtype)

    at: ImportApplicationType = qs.get()

    if not at.is_active:
        raise ValueError(f"Import application of type {at.type} ({at.sub_type}) is not active")

    if form_class is None:
        form_class = CreateImportApplicationForm

    if request.method == "POST":
        form = form_class(request.POST, user=request.user)

        if form.is_valid():
            application = model_class()
            application.importer = form.cleaned_data["importer"]
            application.importer_office = form.cleaned_data["importer_office"]
            application.agent = form.cleaned_data["agent"]
            application.agent_office = form.cleaned_data["agent_office"]
            application.process_type = model_class.PROCESS_TYPE
            application.created_by = request.user
            application.last_updated_by = request.user
            application.application_type = at

            with transaction.atomic():
                application.save()
                Task.objects.create(
                    process=application, task_type=Task.TaskType.PREPARE, owner=request.user
                )

                # Add a draft licence when creating an application
                # Ensures we never have to check for None
                application.licences.create(
                    status=ImportApplicationLicence.Status.DRAFT,
                    issue_paper_licence_only=get_paper_licence_only(at),
                )

            return redirect(
                reverse(application.get_edit_view_name(), kwargs={"application_pk": application.pk})
            )
    else:
        form = form_class(user=request.user)

    context = {
        "form": form,
        "import_application_type": at,
        "application_title": ProcessTypes(model_class.PROCESS_TYPE).label,
        "importers_with_agents": _importers_with_agents(request.user),
        **_get_disabled_application_types(),
    }

    return render(request, "web/domains/case/import/create.html", context)


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def edit_cover_letter(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: ImportApplication = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)

        if request.method == "POST":
            form = CoverLetterForm(request.POST, instance=application)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "case:prepare-response",
                        kwargs={"application_pk": application_pk, "case_type": "import"},
                    )
                )
        else:
            form = CoverLetterForm(instance=application)

        context = {
            "case_type": "import",
            "process": application,
            "task": task,
            "page_title": "Cover Letter Response Preparation",
            "form": form,
        }

        return render(
            request=request,
            template_name="web/domains/case/import/manage/edit-cover-letter.html",
            context=context,
        )


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def edit_licence(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    with transaction.atomic():
        application: ImportApplication = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )
        application_type: ImportApplicationType = application.application_type

        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)

        form_kwargs: dict[str, Any] = {"instance": application.get_most_recent_licence()}

        if application.process_type == OutwardProcessingTradeApplication.PROCESS_TYPE:
            form_class = OPTLicenceForm
            application = application.get_specific_model()
            # Load the data from the opt record
            form_kwargs["initial"] = {"reimport_period": application.reimport_period}

        elif application_type.paper_licence_flag and application_type.electronic_licence_flag:
            form_class = LicenceDateAndPaperLicenceForm

        else:
            form_class = LicenceDateForm

        if request.method == "POST":
            form = form_class(request.POST, **form_kwargs)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "case:prepare-response",
                        kwargs={"application_pk": application_pk, "case_type": "import"},
                    )
                )
        else:
            form = form_class(**form_kwargs)

        context = {
            "case_type": "import",
            "process": application,
            "task": task,
            "page_title": "Licence Response Preparation",
            "form": form,
        }

        return render(
            request=request,
            template_name="web/domains/case/import/manage/edit-licence.html",
            context=context,
        )


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def add_endorsement(request: AuthenticatedHttpRequest, *, application_pk: int) -> HttpResponse:
    return _add_endorsement(request, application_pk, EndorsementChoiceImportApplicationForm)


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def add_custom_endorsement(
    request: AuthenticatedHttpRequest, *, application_pk: int
) -> HttpResponse:
    return _add_endorsement(request, application_pk, EndorsementImportApplicationForm)


def _add_endorsement(
    request: AuthenticatedHttpRequest, application_pk: int, Form: Type[django_forms.ModelForm]
) -> HttpResponse:
    with transaction.atomic():
        application = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)

        if request.method == "POST":
            form = Form(request.POST)

            if form.is_valid():
                endorsement = form.save(commit=False)
                endorsement.import_application = application
                endorsement.save()

                return redirect(
                    reverse(
                        "case:prepare-response",
                        kwargs={"application_pk": application_pk, "case_type": "import"},
                    )
                )
        else:
            form = Form()

        context = {
            "case_type": "import",
            "process": application,
            "task": task,
            "page_title": "Endorsement Response Preparation",
            "form": form,
        }

        return render(
            request=request,
            template_name="web/domains/case/import/manage/add-endorsement.html",
            context=context,
        )


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
def edit_endorsement(
    request: AuthenticatedHttpRequest, *, application_pk: int, endorsement_pk: int
) -> HttpResponse:
    with transaction.atomic():
        application = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )
        endorsement = get_object_or_404(application.endorsements, pk=endorsement_pk)

        task = get_application_current_task(application, "import", Task.TaskType.PROCESS)

        if request.method == "POST":
            form = EndorsementImportApplicationForm(request.POST, instance=endorsement)

            if form.is_valid():
                form.save()

                return redirect(
                    reverse(
                        "case:prepare-response",
                        kwargs={"application_pk": application_pk, "case_type": "import"},
                    )
                )
        else:
            form = EndorsementImportApplicationForm(instance=endorsement)

        context = {
            "case_type": "import",
            "process": application,
            "task": task,
            "page_title": "Endorsement Response Preparation",
            "form": form,
        }

        return render(
            request=request,
            template_name="web/domains/case/import/manage/edit-endorsement.html",
            context=context,
        )


@login_required
@permission_required("web.importer_access", raise_exception=True)
@require_POST
def delete_endorsement(
    request: AuthenticatedHttpRequest, *, application_pk: int, endorsement_pk: int
) -> HttpResponse:
    with transaction.atomic():
        application = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )
        endorsement = get_object_or_404(application.endorsements, pk=endorsement_pk)

        get_application_current_task(application, "import", Task.TaskType.PROCESS)

        if not request.user.has_perm("web.is_contact_of_importer", application.importer):
            raise PermissionDenied

        endorsement.delete()

        return redirect(
            reverse(
                "case:prepare-response",
                kwargs={"application_pk": application_pk, "case_type": "import"},
            )
        )


# TODO: This can be replaced by the following:
# icms/web/domains/case/views.py -> def view_application_file
def view_file(request, application, related_file_model, file_pk):
    has_perm_importer = request.user.has_perm("web.importer_access")
    has_perm_ilb_admin = request.user.has_perm("web.ilb_admin")

    if not has_perm_importer and not has_perm_ilb_admin:
        raise PermissionDenied

    # first check is for case managers (who are not marked as contacts of
    # importers), second is for people submitting applications
    if not has_perm_ilb_admin and not request.user.has_perm(
        "web.is_contact_of_importer", application.importer
    ):
        raise PermissionDenied

    document = related_file_model.get(pk=file_pk)
    file_content = get_file_from_s3(document.path)

    response = HttpResponse(content=file_content, content_type=document.content_type)
    response["Content-Disposition"] = f'attachment; filename="{document.filename}"'

    return response


@login_required
@permission_required("web.ilb_admin", raise_exception=True)
@require_POST
def bypass_chief(
    request: AuthenticatedHttpRequest, *, application_pk: int, chief_status: str
) -> HttpResponse:
    if not settings.ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD:
        raise PermissionDenied

    with transaction.atomic():
        application: ImportApplication = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, "import", Task.TaskType.CHIEF_WAIT)
        task.is_active = False
        task.finished = timezone.now()
        task.owner = request.user
        task.save()

        if chief_status == "success":
            # TODO: The "real" chief success will have to do this too.
            if application.status == ImportApplication.Statuses.VARIATION_REQUESTED:
                vr = application.variation_requests.get(status=VariationRequest.OPEN)
                vr.status = VariationRequest.ACCEPTED
                vr.save()

            application.status = ImportApplication.Statuses.COMPLETED
            application.save()

            create_acknowledge_notification_task(application, task)

        elif chief_status == "failure":
            Task.objects.create(
                process=application, task_type=Task.TaskType.CHIEF_ERROR, previous=task
            )

        messages.success(
            request,
            f"CHIEF: faked {chief_status} for application {application.get_reference()}.",
        )

        return redirect(reverse("workbasket"))


class IMICaseListView(PermissionRequiredMixin, LoginRequiredMixin, ListView):
    permission_required = "web.ilb_admin"
    template_name = "web/domains/case/import/imi/list.html"
    context_object_name = "imi_list"

    def get_queryset(self) -> "QuerySet[ImportApplication]":
        """Return all applications that have been acknowledged."""

        # TODO: ICMSLST-809 Revisit when the licence file has been generated (to filter on correct task)
        imi_eu_countries = CountryGroup.objects.get(name="EU Countries (IMI Cases)").countries.all()

        qs = (
            ImportApplication.objects.filter(
                application_type__type=ImportApplicationType.Types.FIREARMS,
                tasks__task_type=Task.TaskType.ACK,
                importer_office__postcode__istartswith="BT",
                consignment_country__in=imi_eu_countries,
                imi_submitted_by__isnull=True,
            )
            .annotate(
                authorised_date=models.F("tasks__created"),
                import_contacts=ArrayAgg(
                    Concat(
                        models.F("importcontact__first_name"),
                        models.Value(" "),
                        models.F("importcontact__last_name"),
                    ),
                ),
            )
            .values_list("pk", "reference", "import_contacts", "authorised_date", named=True)
        )

        return qs

    def get_context_data(self, **kwargs: dict[Any, Any]) -> dict[Any, Any]:
        context = super().get_context_data(**kwargs)
        context["page_title"] = "IMI Applications"

        return context


class IMICaseDetailView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    template_name = "web/domains/case/manage/imi-case-detail.html"
    permission_required = "web.ilb_admin"
    pk_url_kwarg = "application_pk"
    context_object_name = "process"
    queryset = ImportApplication.objects.select_related(
        "importer", "importer_office", "case_owner", "application_type", "contact"
    )

    def get_context_data(self, **kwargs):
        context = {
            "page_title": f"Case {self.object.get_reference()}",
            "case_type": "import",
            "contacts": self.object.importcontact_set.all(),
            "licence": self.object.get_most_recent_licence(),
        }

        return super().get_context_data(**kwargs) | context


@require_POST
@permission_required("web.ilb_admin", raise_exception=True)
@login_required
def imi_confirm_provided(request: AuthenticatedHttpRequest, *, application_pk) -> HttpResponse:
    """Indicates the relevant details have been sent to IMI."""

    with transaction.atomic():
        application: ImportApplication = get_object_or_404(
            ImportApplication.objects.select_for_update(), pk=application_pk
        )

        application.imi_submitted_by = request.user
        application.imi_submit_datetime = timezone.now()
        application.save()

    return redirect(reverse("import:imi-case-detail", kwargs={"application_pk": application_pk}))
