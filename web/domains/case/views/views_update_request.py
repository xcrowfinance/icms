from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from guardian.shortcuts import get_users_with_perms

from web.domains.template.models import Template
from web.flow.models import Task
from web.notify import email
from web.types import AuthenticatedHttpRequest

from .. import forms, models
from ..types import ImpOrExp
from ..utils import (
    check_application_permission,
    get_application_current_task,
    get_case_page_title,
)
from .utils import get_class_imp_or_exp


@login_required
@permission_required("web.reference_data_access", raise_exception=True)
def manage_update_requests(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        task = get_application_current_task(application, case_type, Task.TaskType.PROCESS)

        if case_type == "import":
            template_code = "IMA_APP_UPDATE"

            placeholder_content = {
                "CASE_REFERENCE": application.reference,
                "IMPORTER_NAME": application.importer.display_name,
                "CASE_OFFICER_NAME": request.user,
            }
        elif case_type == "export":
            template_code = "CA_APPLICATION_UPDATE_EMAIL"

            placeholder_content = {
                "CASE_REFERENCE": application.reference,
                "EXPORTER_NAME": application.exporter.name,
                "CASE_OFFICER_NAME": request.user,
            }
        else:
            raise NotImplementedError(
                f"case type {case_type} is not implemented for update requests"
            )

        template = Template.objects.get(template_code=template_code, is_active=True)
        email_subject = template.get_title({"CASE_REFERENCE": application.reference})
        email_content = template.get_content(placeholder_content)

        if request.POST:
            form = forms.UpdateRequestForm(request.POST)
            if form.is_valid():
                update_request = form.save(commit=False)
                update_request.requested_by = request.user
                update_request.request_datetime = timezone.now()
                update_request.status = models.UpdateRequest.Status.OPEN
                update_request.save()

                application.update_requests.add(update_request)

                task.is_active = False
                task.finished = timezone.now()
                task.save()

                Task.objects.create(
                    process=application, task_type=Task.TaskType.PREPARE, previous=task
                )

                if case_type == "import":
                    contacts = get_users_with_perms(
                        application.importer, only_with_perms_in=["is_contact_of_importer"]
                    ).filter(user_permissions__codename="importer_access")
                elif case_type == "export":
                    contacts = get_users_with_perms(
                        application.exporter, only_with_perms_in=["is_contact_of_exporter"]
                    ).filter(user_permissions__codename="exporter_access")
                else:
                    raise NotImplementedError(
                        f"case type {case_type} is not implemented for update requests"
                    )

                recipients = list(contacts.values_list("email", flat=True))

                email.send_email.delay(
                    update_request.request_subject,
                    update_request.request_detail,
                    recipients,
                    update_request.email_cc_address_list,
                )

                return redirect(reverse("workbasket"))
        else:
            form = forms.UpdateRequestForm(
                initial={
                    "request_subject": email_subject,
                    "request_detail": email_content,
                }
            )

        update_requests = application.update_requests.filter(is_active=True)
        update_request = update_requests.filter(
            status__in=[models.UpdateRequest.Status.OPEN, models.UpdateRequest.Status.RESPONDED]
        ).first()
        previous_update_requests = update_requests.filter(status=models.UpdateRequest.Status.CLOSED)

        context = {
            "process": application,
            "task": task,
            "page_title": get_case_page_title(case_type, application, "Update Requests"),
            "form": form,
            "previous_update_requests": previous_update_requests,
            "update_request": update_request,
            "case_type": case_type,
        }

        return render(
            request=request,
            template_name="web/domains/case/manage/update-requests.html",
            context=context,
        )


@login_required
@permission_required("web.reference_data_access", raise_exception=True)
@require_POST
def close_update_request(
    request: AuthenticatedHttpRequest,
    *,
    application_pk: int,
    update_request_pk: int,
    case_type: str,
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        get_application_current_task(application, case_type, Task.TaskType.PROCESS)

        update_request = get_object_or_404(application.update_requests, pk=update_request_pk)

        update_request.status = models.UpdateRequest.Status.CLOSED
        update_request.closed_by = request.user
        update_request.closed_datetime = timezone.now()
        update_request.save()

    return redirect(
        reverse(
            "case:manage-update-requests",
            kwargs={"application_pk": application_pk, "case_type": case_type},
        )
    )


@login_required
def start_update_request(
    request: AuthenticatedHttpRequest, *, application_pk: int, update_request_pk=int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, case_type)

        get_application_current_task(application, case_type, Task.TaskType.PREPARE)

        update_requests = application.update_requests.filter(is_active=True)
        update_request = get_object_or_404(
            update_requests.filter(is_active=True).filter(status=models.UpdateRequest.Status.OPEN),
            pk=update_request_pk,
        )
        previous_update_requests = update_requests.filter(status=models.UpdateRequest.Status.CLOSED)

        if request.POST:
            update_request.status = models.UpdateRequest.Status.UPDATE_IN_PROGRESS
            update_request.save()

            return redirect(
                reverse(application.get_edit_view_name(), kwargs={"application_pk": application_pk})
            )

        context = {
            "process": application,
            "process_template": f"web/domains/case/{case_type}/partials/process.html",
            "case_type": case_type,
            "update_request": update_request,
            "previous_update_requests": previous_update_requests,
        }

        return render(
            request=request,
            template_name="web/domains/case/start-update-request.html",
            context=context,
        )


@login_required
def respond_update_request(
    request: AuthenticatedHttpRequest, *, application_pk: int, case_type: str
) -> HttpResponse:
    model_class = get_class_imp_or_exp(case_type)

    with transaction.atomic():
        application: ImpOrExp = get_object_or_404(
            model_class.objects.select_for_update(), pk=application_pk
        )

        check_application_permission(application, request.user, case_type)

        get_application_current_task(application, case_type, Task.TaskType.PREPARE)

        update_requests = application.update_requests.filter(is_active=True)
        update_request = update_requests.get(
            status__in=[
                models.UpdateRequest.Status.UPDATE_IN_PROGRESS,
                models.UpdateRequest.Status.RESPONDED,
            ]
        )
        previous_update_requests = update_requests.filter(status=models.UpdateRequest.Status.CLOSED)

        if request.POST:
            form = forms.UpdateRequestResponseForm(request.POST, instance=update_request)
            if form.is_valid():
                update_request = form.save(commit=False)
                update_request.status = models.UpdateRequest.Status.RESPONDED

                update_request.response_by = request.user
                update_request.response_datetime = timezone.now()
                update_request.save()

                return redirect(
                    reverse(
                        application.get_edit_view_name(), kwargs={"application_pk": application_pk}
                    )
                )
        else:
            form = forms.UpdateRequestResponseForm(instance=update_request)

        context = {
            "process": application,
            "process_template": f"web/domains/case/{case_type}/partials/process.html",
            "case_type": case_type,
            "form": form,
            "update_request": update_request,
            "previous_update_requests": previous_update_requests,
        }

        return render(
            request=request,
            template_name="web/domains/case/respond-update-request.html",
            context=context,
        )