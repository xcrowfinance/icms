from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Window
from django.db.models.functions import RowNumber
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, UpdateView

from web.domains.case.forms import VariationRequestForm
from web.domains.case.models import VariationRequest
from web.domains.case.shared import ImpExpStatus
from web.domains.case.types import ImpOrExp
from web.domains.case.utils import check_application_permission
from web.flow.models import Process, Task

from .mixins import ApplicationAndTaskRelatedObjectMixin
from .utils import get_current_task_and_readonly_status


class VariationRequestManageView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    """Case management view for viewing application variations."""

    # PermissionRequiredMixin config
    permission_required = ["web.ilb_admin"]

    # DetailView config
    model = Process
    pk_url_kwarg = "application_pk"
    template_name = "web/domains/case/manage/variations-manage.html"

    def get_context_data(self, **kwargs):
        application = self.object.get_specific_model()
        case_type = self.kwargs["case_type"]

        task, readonly_view = get_current_task_and_readonly_status(
            application,
            case_type,
            self.request.user,
            Task.TaskType.PROCESS,
            select_for_update=False,
        )

        context = super().get_context_data(**kwargs)

        variation_requests = application.variation_requests.order_by(
            "-requested_datetime"
        ).annotate(vr_num=Window(expression=RowNumber()))

        return context | {
            "page_title": f"Variations {application.get_reference()}",
            "process": application,
            "case_type": case_type,
            "readonly_view": readonly_view,
            "variation_requests": variation_requests,
        }


@method_decorator(transaction.atomic, name="post")
class VariationRequestCancelView(
    ApplicationAndTaskRelatedObjectMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView
):
    """Case management view for cancelling a request variation.

    This is called when the variation was raised in error.
    """

    # ApplicationAndTaskRelatedObjectMixin
    current_status = [ImpExpStatus.VARIATION_REQUESTED]
    current_task_type = Task.TaskType.PROCESS

    next_status = ImpExpStatus.COMPLETED
    next_task_type = Task.TaskType.ACK

    # PermissionRequiredMixin config
    permission_required = ["web.ilb_admin"]

    # UpdateView config
    success_url = reverse_lazy("workbasket")
    pk_url_kwarg = "variation_request_pk"
    model = VariationRequest
    fields = ["reject_cancellation_reason"]
    template_name = "web/domains/case/manage/variations-cancel.html"

    # Extra typing for clarity
    object: VariationRequest
    application: ImpOrExp
    task: Task

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        return context | {
            "page_title": f"Variations {self.application.get_reference()}",
            "case_type": self.kwargs["case_type"],
            "process": self.application,
            "vr_num": self.application.variation_requests.count(),
        }

    def form_valid(self, form: ModelForm) -> HttpResponseRedirect:
        result = super().form_valid(form)

        # Having saved the cancellation reason we need to do a few things
        self.object.refresh_from_db()
        self.object.status = VariationRequest.CANCELLED
        self.object.closed_datetime = timezone.now()
        self.object.closed_by = self.request.user
        self.object.save()

        self.update_application_status()
        self.update_application_tasks()

        return result


@method_decorator(transaction.atomic, name="post")
class VariationRequestRequestUpdateView(
    ApplicationAndTaskRelatedObjectMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView
):
    """Case management view for requesting an update from the applicant regarding the variation request."""

    # ApplicationAndTaskRelatedObjectMixin Config
    current_status = [ImpExpStatus.VARIATION_REQUESTED]
    current_task_type = None  # We will not be updating any existing tasks
    next_status = None  # We will not be updating the status
    next_task_type = Task.TaskType.VR_REQUEST_CHANGE

    # UpdateView config
    pk_url_kwarg = "variation_request_pk"
    model = VariationRequest
    fields = ["update_request_reason"]
    template_name = "web/domains/case/manage/variations-request-update.html"

    # Extra typing for clarity
    object: VariationRequest

    def has_permission(self):
        application = Process.objects.get(
            pk=self.kwargs["application_pk"]  # type: ignore[attr-defined]
        ).get_specific_model()

        try:
            check_application_permission(application, self.request.user, self.kwargs["case_type"])
        except PermissionDenied:
            return False

        return True

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        return context | {
            "page_title": f"Variations {self.application.get_reference()}",
            "case_type": self.kwargs["case_type"],
            "process": self.application,
            "vr_num": self.application.variation_requests.count(),
        }

    def form_valid(self, form: ModelForm) -> HttpResponseRedirect:
        result = super().form_valid(form)

        self.update_application_tasks()

        return result

    def get_success_url(self):
        return reverse(
            "case:variation-request-manage",
            kwargs={"application_pk": self.application.pk, "case_type": self.kwargs["case_type"]},
        )


@method_decorator(transaction.atomic, name="post")
class VariationRequestRespondToUpdateRequestView(
    ApplicationAndTaskRelatedObjectMixin, PermissionRequiredMixin, LoginRequiredMixin, UpdateView
):
    """View used by applicant to update a variation request."""

    current_status = [ImpExpStatus.VARIATION_REQUESTED]
    current_task_type = Task.TaskType.VR_REQUEST_CHANGE

    # UpdateView config
    model = VariationRequest
    pk_url_kwarg = "variation_request_pk"
    form_class = VariationRequestForm
    success_url = reverse_lazy("workbasket")
    template_name = "web/domains/case/variation-request-update.html"

    # Extra typing for clarity
    object: VariationRequest

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        return context | {
            "page_title": f"Variations {self.application.get_reference()}",
            "case_type": self.kwargs["case_type"],
            "process": self.application,
            "vr_num": self.application.variation_requests.count(),
        }

    def form_valid(self, form: ModelForm) -> HttpResponseRedirect:
        result = super().form_valid(form)

        # Having saved the variation request changes we need to do a few things
        self.object.refresh_from_db()
        self.object.update_request_reason = None
        self.object.save()

        self.update_application_tasks()

        return result

    def has_permission(self):
        application = Process.objects.get(
            pk=self.kwargs["application_pk"]  # type: ignore[attr-defined]
        ).get_specific_model()

        try:
            check_application_permission(application, self.request.user, self.kwargs["case_type"])
        except PermissionDenied:
            return False

        return True