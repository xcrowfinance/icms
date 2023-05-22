from collections.abc import Collection
from typing import Any

import html2text
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models import QuerySet
from django.utils import timezone

from config.celery import app
from web.auth.utils import get_ilb_admin_users
from web.domains.case.types import ImpOrExp
from web.domains.template.utils import get_email_template_subject_body
from web.models import CaseEmail, Exporter, Importer, User, WithdrawApplication
from web.permissions import get_org_obj_permissions, organisation_get_contacts
from web.utils.s3 import get_file_from_s3, get_s3_client

from . import utils
from .constants import DatabaseEmailTemplate


@app.task(name="web.notify.email.send_email")
def send_email(
    subject: str,
    body: str,
    recipients: Collection[str],
    cc: Collection[str] = (),
    attachments: Collection[tuple[str, bytes]] = (),
    html_message: str | None = None,
):
    message = EmailMultiAlternatives(
        subject, body, settings.EMAIL_FROM, recipients, cc=cc, attachments=attachments
    )

    if html_message:
        message.attach_alternative(html_message, "text/html")

    message.send()


def send_to_contacts(
    subject: str, message: str, contacts: QuerySet[User], html_message: str | None = None
) -> None:
    for contact in contacts:
        send_email.delay(
            subject, message, utils.get_notification_emails(contact), html_message=html_message
        )


def send_to_importer_contacts(
    importer: Importer, subject: str, message: str, html_message: str | None = None
) -> None:
    if importer.type == Importer.INDIVIDUAL:
        # TODO: ICMSLST-1948 Revisit this (importer.user is something that should be removed.)
        if importer.user and importer.user.account_status == User.ACTIVE:
            send_email.delay(
                subject,
                message,
                utils.get_notification_emails(importer.user),
                html_message=html_message,
            )

        return

    obj_perms = get_org_obj_permissions(importer)
    contacts = organisation_get_contacts(importer, perms=[obj_perms.is_contact.codename])
    send_to_contacts(subject, message, contacts, html_message)


def send_to_all_importers(subject: str, message: str, html_message: str | None = None) -> None:
    importers = Importer.objects.filter(is_active=True)
    for importer in importers:
        send_to_importer_contacts(importer, subject, message, html_message)


def send_to_exporter_contacts(
    exporter: Exporter, subject: str, message: str, html_message: str | None = None
) -> None:
    obj_perms = get_org_obj_permissions(exporter)

    # TODO ICMSLST-1968 is_contact perm deprecated
    contacts = organisation_get_contacts(exporter, perms=[obj_perms.is_contact.codename])
    send_to_contacts(subject, message, contacts, html_message)


def send_to_all_exporters(subject: str, message: str, html_message: str | None = None) -> None:
    exporters = Exporter.objects.filter(is_active=True)
    for exporter in exporters:
        send_to_exporter_contacts(exporter, subject, message, html_message)


def send_to_application_contacts(
    application: ImpOrExp, subject: str, message: str, html_message: str | None = None
) -> None:
    if application.is_import_application():
        org = application.agent or application.importer
    else:
        org = application.agent or application.exporter

    obj_perms = get_org_obj_permissions(org)
    contacts = organisation_get_contacts(org, perms=[obj_perms.edit.codename])

    send_to_contacts(subject, message, contacts, html_message)


def send_to_case_officers(application, subject, message, html_message=None):
    if application.case_owner:
        send_email.delay(
            subject,
            message,
            utils.get_notification_emails(application.case_owner),
            html_message=html_message,
        )
    else:
        send_to_contacts(subject, message, get_ilb_admin_users(), html_message)


@app.task(name="web.notify.email.send_mailshot")
def send_mailshot(subject, message, html_message=None, to_importers=False, to_exporters=False):
    """
    Sends mailshots
    """
    if to_importers:
        send_to_all_importers(subject, message, html_message=html_message)
    if to_exporters:
        send_to_all_exporters(subject, message, html_message=html_message)


def send_case_email(case_email: CaseEmail) -> None:
    attachments = []
    s3_client = get_s3_client()

    for document in case_email.attachments.all():
        file_content = get_file_from_s3(document.path, client=s3_client)
        attachments.append((document.filename, file_content))

    send_email(
        case_email.subject,
        case_email.body,
        [case_email.to],
        case_email.cc_address_list,
        attachments,
    )

    case_email.status = CaseEmail.Status.OPEN
    case_email.sent_datetime = timezone.now()
    case_email.save()


def send_refused_email(application: ImpOrExp) -> None:
    context = {
        "application": application,
        "subject": f"Application reference {application.reference} has been refused by ILB.",
    }
    template = "email/application/refused.html"
    send_html_email(application, template, context)


def send_reassign_email(application: ImpOrExp, comment: str) -> None:
    context = {
        "subject": f"ICMS Case Ref. {application.reference} has been assigned to you",
        "comment": comment,
        "reference": application.reference,
    }
    send_html_email(
        application,
        "email/application/reassigned.html",
        context,
        [application.case_owner],
    )


def send_html_email(
    application: ImpOrExp,
    template: str,
    context: dict[str, Any],
    contacts: list[User] | None = None,
):
    message_html = utils.render_email(template, context)
    message_text = html2text.html2text(message_html)

    if contacts:
        send_to_contacts(context["subject"], message_text, contacts, message_html)
    else:
        send_to_application_contacts(application, context["subject"], message_text, message_html)


def get_withdrawal_email_subject(withdrawal: WithdrawApplication, application: ImpOrExp) -> str:
    status = ""
    if withdrawal.status == WithdrawApplication.Statuses.DELETED:
        status = " Cancelled"
    elif withdrawal.status != WithdrawApplication.Statuses.OPEN:
        status = " " + withdrawal.get_status_display().title()
    return f"Withdrawal Request{status}: {application.reference}"


def send_withdrawal_email(withdrawal: WithdrawApplication) -> None:
    contacts = None

    if withdrawal.status not in WithdrawApplication.Statuses:
        return

    if withdrawal.status in [
        WithdrawApplication.Statuses.OPEN,
        WithdrawApplication.Statuses.DELETED,
    ]:
        contacts = get_ilb_admin_users()

    application = withdrawal.export_application or withdrawal.import_application
    subject = get_withdrawal_email_subject(withdrawal, application)

    context = {
        "withdrawal_reason": withdrawal.response,
        "subject": subject,
        "application": application,
    }
    template_name = f"email/application/withdraw/{withdrawal.status}.html"
    send_html_email(application, template_name, context, contacts=contacts)


def send_database_email(application: ImpOrExp, template_name: DatabaseEmailTemplate) -> None:
    subject, body = get_email_template_subject_body(application, template_name)
    send_to_application_contacts(application, subject, body)
