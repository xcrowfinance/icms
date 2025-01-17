import http
import json
from typing import Any

import mohawk
import mohawk.exc
import pydantic
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core import exceptions
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.crypto import constant_time_compare
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, TemplateView, View
from mohawk.util import parse_authorization_header, prepare_header_val

from web.domains.case.services import case_progress
from web.domains.case.shared import ImpExpStatus
from web.domains.case.tasks import create_case_document_pack
from web.domains.case.views.mixins import ApplicationTaskMixin
from web.models import (
    CaseDocumentReference,
    ICMSHMRCChiefRequest,
    ImportApplication,
    ImportApplicationLicence,
    Task,
)
from web.permissions import Perms
from web.types import AuthenticatedHttpRequest
from web.utils.sentry import capture_exception, capture_message

from . import client, types, utils

HAWK_ALGO = "sha256"
HAWK_RESPONSE_HEADER = "Server-Authorization"


def get_credentials_map(access_id: str) -> dict[str, Any]:
    if not constant_time_compare(access_id, settings.HAWK_AUTH_ID):
        raise mohawk.exc.HawkFail(f"Invalid Hawk ID {access_id}")

    return {
        "id": settings.HAWK_AUTH_ID,
        "key": settings.HAWK_AUTH_KEY,
        "algorithm": HAWK_ALGO,
    }


def validate_request(request: HttpRequest) -> mohawk.Receiver:
    """Raise Django's BadRequest if the request has invalid credentials."""

    try:
        auth_token = request.headers.get("HAWK_AUTHENTICATION")

        if not auth_token:
            raise KeyError
    except KeyError as err:
        raise exceptions.BadRequest from err

    # ICMS-HMRC creates the payload hash before encoding the json, therefore decode it here to get the same hash.
    content = request.body.decode()

    try:
        return mohawk.Receiver(
            get_credentials_map,
            auth_token,
            request.build_absolute_uri(),
            request.method,
            content=content,
            content_type=request.content_type,
            seen_nonce=utils.seen_nonce,
        )
    except mohawk.exc.HawkFail as err:
        raise exceptions.BadRequest from err


# Hawk view (no CSRF)
@method_decorator(csrf_exempt, name="dispatch")
class HawkViewBase(View):
    def dispatch(self, *args: Any, **kwargs: Any) -> JsonResponse:
        try:
            # Validate sender request
            hawk_receiver = validate_request(self.request)

            # Create response
            response = super().dispatch(*args, **kwargs)

        except (pydantic.ValidationError, exceptions.BadRequest):
            capture_exception()

            return JsonResponse({}, status=http.HTTPStatus.BAD_REQUEST)

        except Exception:
            capture_exception()

            return JsonResponse({}, status=http.HTTPStatus.UNPROCESSABLE_ENTITY)

        # Create and set the response header
        hawk_response_header = self._get_hawk_response_header(hawk_receiver, response)
        response.headers[HAWK_RESPONSE_HEADER] = hawk_response_header

        # return the response
        return response

    def _get_hawk_response_header(
        self, hawk_receiver: mohawk.Receiver, response: JsonResponse
    ) -> str:
        sender_nonce = hawk_receiver.parsed_header.get("nonce")

        hawk_response_header = hawk_receiver.respond(
            content=response.content, content_type=response.headers["Content-type"]
        )

        # Add the original sender nonce and ts to get around this bug
        # https://github.com/kumar303/mohawk/issues/50
        if not parse_authorization_header(hawk_response_header).get("nonce"):
            sender_nonce = prepare_header_val(sender_nonce)
            ts = prepare_header_val(str(timezone.now().timestamp()))

            hawk_response_header = f'{hawk_response_header}, nonce="{sender_nonce}", ts="{ts}"'

        return hawk_response_header


class LicenseDataCallback(HawkViewBase):
    """View used by ICMS-HMRC to send licence data back to ICMS."""

    # View Config
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        licence_replies = types.ChiefLicenceReplyResponseData.model_validate_json(request.body)

        with transaction.atomic():
            for accepted in licence_replies.accepted:
                self.accept_application(accepted)

            for rejected in licence_replies.rejected:
                self.reject_application(rejected)

        return JsonResponse({}, status=http.HTTPStatus.OK)

    def accept_application(self, accepted_licence: types.AcceptedLicence) -> None:
        chief_req = self.get_chief_request(accepted_licence.id)

        utils.chief_licence_reply_approve_licence(chief_req.import_application)
        utils.complete_chief_request(chief_req)

    def reject_application(self, rejected_licence: types.RejectedLicence) -> None:
        chief_req = self.get_chief_request(rejected_licence.id)

        utils.chief_licence_reply_reject_licence(chief_req.import_application)
        utils.fail_chief_request(chief_req, rejected_licence.errors)

    @staticmethod
    def get_chief_request(icms_hmrc_id: str) -> ICMSHMRCChiefRequest:
        chief_req = (
            ICMSHMRCChiefRequest.objects.select_related("import_application")
            .select_for_update()
            .get(icms_hmrc_id=icms_hmrc_id)
        )

        return chief_req


class UsageDataCallbackView(HawkViewBase):
    """View used by ICMS-HMRC to send usage data back to ICMS."""

    # View Config
    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        response = types.ChiefUsageDataResponseData.model_validate_json(request.body)

        with transaction.atomic():
            for rec in response.usage_data:
                self._update_import_application_usage_status(rec)

        return JsonResponse({}, status=http.HTTPStatus.OK)

    def _update_import_application_usage_status(self, rec: types.UsageRecord) -> None:
        try:
            licence = ImportApplicationLicence.objects.get(
                status=ImportApplicationLicence.Status.ACTIVE,
                document_references__document_type=CaseDocumentReference.Type.LICENCE,
                document_references__reference=rec.licence_ref,
            )
        except ObjectDoesNotExist:
            capture_message(
                f"licence not found: Unable to set usage status for licence number: {rec.licence_ref}."
            )
            return

        application = licence.import_application
        application.chief_usage_status = rec.licence_status
        application.save()


@method_decorator(transaction.atomic, name="post")
class ResendLicenceToChiefView(
    ApplicationTaskMixin,
    PermissionRequiredMixin,
    LoginRequiredMixin,
    View,
):
    """View to resend a Licence to CHIEF."""

    # ApplicationTaskMixin
    current_status = [
        ImpExpStatus.VARIATION_REQUESTED,
        ImpExpStatus.PROCESSING,
        ImpExpStatus.REVOKED,
    ]
    current_task_type = Task.TaskType.CHIEF_ERROR

    # Only applies to applications being processed
    next_task_type = Task.TaskType.DOCUMENT_SIGNING

    # PermissionRequiredMixin
    permission_required = [Perms.sys.ilb_admin]

    # View
    http_method_names = ["post"]

    def post(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.set_application_and_task()

        if self.application.status == ImpExpStatus.REVOKED:
            client.send_application_to_chief(self.application, self.task, revoke_licence=True)
            messages.success(request, "Revoke licence request send to CHIEF for processing")

        else:
            # Update the current task so `create_case_document_pack` will work correctly
            self.update_application_tasks()

            # Regenerating the licence document pack will send the application to CHIEF
            # after the updated documents have been created.
            create_case_document_pack(self.application, self.request.user)

            messages.success(
                request,
                "Once the licence has been regenerated it will be send to CHIEF for processing",
            )

        return redirect("chief:failed-licences")


@method_decorator(transaction.atomic, name="post")
class RevertLicenceToProcessingView(
    ApplicationTaskMixin, PermissionRequiredMixin, LoginRequiredMixin, View
):
    """View to revert an application with a chief error back to being processed by ILB.

    This can be useful if there is an error in the data and ICMS-HMRC has rejected it.
    """

    # ApplicationTaskMixin
    current_status = [ImpExpStatus.VARIATION_REQUESTED, ImpExpStatus.PROCESSING]
    current_task_type = Task.TaskType.CHIEF_ERROR

    next_task_type = Task.TaskType.PROCESS

    # PermissionRequiredMixin
    permission_required = [Perms.sys.ilb_admin]

    # View
    http_method_names = ["post"]

    def post(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.set_application_and_task()

        self.update_application_tasks()
        self.application.update_order_datetime()
        self.application.save()

        messages.success(request, "Licence now back in processing so the error can be corrected.")

        return redirect("chief:failed-licences")


class _BaseTemplateView(PermissionRequiredMixin, TemplateView):
    permission_required = Perms.sys.ilb_admin

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # We need the counts for each type to show in the navigation tabs.
        failed_licences = ImportApplication.objects.filter(
            tasks__task_type=Task.TaskType.CHIEF_ERROR, tasks__is_active=True
        )
        pending_licences = ImportApplication.objects.filter(
            tasks__task_type__in=[Task.TaskType.CHIEF_WAIT, Task.TaskType.CHIEF_REVOKE_WAIT],
            tasks__is_active=True,
        )

        context = {
            "failed_licences_count": failed_licences.count(),
            "failed_licences": failed_licences,
            "pending_licences_count": pending_licences.count(),
            "pending_licences": pending_licences,
        }

        return super().get_context_data(**kwargs) | context


class PendingLicences(_BaseTemplateView):
    """Licences that have been sent to ICMS-HMRC and therefore CHIEF."""

    template_name = "web/domains/chief/pending_licences.html"


class FailedLicences(_BaseTemplateView):
    """Licences that have failed for reasons that are application specific.

    CHIEF protocol errors (file errors) should be handled in ICMS-HMRC.
    """

    template_name = "web/domains/chief/failed_licences.html"


class ChiefRequestDataView(PermissionRequiredMixin, DetailView):
    permission_required = Perms.sys.ilb_admin
    http_method_names = ["get"]
    pk_url_kwarg = "icmshmrcchiefrequest_id"
    model = ICMSHMRCChiefRequest

    def get(self, request: AuthenticatedHttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        return JsonResponse(data=self.get_object().request_data)


class CheckChiefProgressView(
    ApplicationTaskMixin, PermissionRequiredMixin, LoginRequiredMixin, View
):
    # View Config
    http_method_names = ["get"]

    # ApplicationTaskMixin Config
    current_status = [
        ImpExpStatus.PROCESSING,
        ImpExpStatus.VARIATION_REQUESTED,
        ImpExpStatus.COMPLETED,
        ImpExpStatus.REVOKED,
    ]

    # PermissionRequiredMixin Config
    permission_required = [Perms.sys.ilb_admin]

    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        self.set_application_and_task()

        active_tasks = case_progress.get_active_task_list(self.application)
        reload_workbasket = False

        if self.application.status == ImpExpStatus.COMPLETED:
            msg = "Accepted - An accepted response has been received from CHIEF."
            reload_workbasket = True

        elif Task.TaskType.CHIEF_ERROR in active_tasks:
            msg = "Rejected - A rejected response has been received from CHIEF."
            reload_workbasket = True

        elif Task.TaskType.CHIEF_WAIT in active_tasks:
            msg = "Awaiting Response - Licence sent to CHIEF, we are awaiting a response"

        elif self.application.status == ImpExpStatus.REVOKED:
            if Task.TaskType.CHIEF_REVOKE_WAIT in active_tasks:
                msg = "Awaiting Response - Licence sent to CHIEF, we are awaiting a response"
            else:
                msg = "Accepted - An accepted response has been received from CHIEF."
                reload_workbasket = True

        else:
            raise Exception("Unknown state for application")

        return JsonResponse(data={"msg": msg, "reload_workbasket": reload_workbasket})


class CheckICMSConnectionView(HawkViewBase):
    """View used by ICMS-HMRC to test connection to ICMS"""

    http_method_names = ["post"]

    def post(self, request: HttpRequest, *args: Any, **kwargs: Any) -> JsonResponse:
        data = json.loads(request.body.decode("utf-8"))

        if data != {"foo": "bar"}:
            error_msg = f"Invalid request data: {data}"

            return JsonResponse(status=http.HTTPStatus.BAD_REQUEST, data={"errors": error_msg})

        return JsonResponse(status=http.HTTPStatus.OK, data={"bar": "foo"})
