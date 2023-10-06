import datetime as dt
from typing import Any, Literal

import html2text
import structlog as logging
from django.conf import settings
from django.contrib.postgres.aggregates import StringAgg
from django.utils import timezone

from config.celery import app
from web.domains.case.services import document_pack
from web.models import (
    AccessRequest,
    Constabulary,
    DFLApplication,
    ExportApplication,
    FirearmsAuthority,
    FurtherInformationRequest,
    ImportApplication,
    Importer,
    Process,
    Section5Authority,
    User,
)
from web.permissions import Perms, SysPerms, constabulary_get_contacts

from . import email, utils

logger = logging.getLogger(__name__)


def send_notification(
    subject: str,
    template: str,
    context: dict[str, Any] | None = None,
    recipients: list[str] | None = None,
    cc_list: list[str] | None = None,
    attachment_ids: tuple[int, ...] = (),
):
    """Renders given email template and sends to recipients.

    User's personal and alternative emails with portal notifications
    enabled will be used.

    Emails are queued to Redis to be sent asynchronously"""

    html_message = utils.render_email(template, context)
    message_text = html2text.html2text(html_message)
    email.send_email.delay(
        subject,
        message_text,
        recipients,
        html_message=html_message,
        cc=cc_list,
        attachment_ids=attachment_ids,
    )


def register(user, password):
    subject = "Import Case Management System Account"
    send_notification(
        subject,
        "email/registration/registration.html",
        context={
            "password": password,
            "username": user.username,
            "name": user.full_name,
            "first_name": user.first_name,
        },
        recipients=utils.get_notification_emails(user),
    )


def mailshot(mailshot):
    html_message = utils.render_email(
        "email/mailshot/mailshot.html",
        {"subject": mailshot.email_subject, "body": mailshot.email_body},
    )
    message_text = html2text.html2text(html_message)
    email.send_mailshot.delay(
        f"{mailshot.email_subject}",
        message_text,
        html_message=html_message,
        to_importers=mailshot.is_to_importers,
        to_exporters=mailshot.is_to_exporters,
    )


def retract_mailshot(mailshot):
    html_message = utils.render_email(
        "email/mailshot/mailshot.html",
        {
            "subject": mailshot.retract_email_subject,
            "body": mailshot.retract_email_body,
        },
    )
    message_text = html2text.html2text(html_message)
    email.send_mailshot.delay(
        f"{mailshot.retract_email_subject}",
        message_text,
        html_message=html_message,
        to_importers=mailshot.is_to_importers,
        to_exporters=mailshot.is_to_exporters,
    )


def send_fir_to_contacts(
    process: Process,
    fir: FurtherInformationRequest,
    context: dict[str, str],
    attachment_ids: tuple[int, ...] = (),
) -> None:
    match process:
        case AccessRequest():
            contacts = [process.submitted_by]
        case ImportApplication() | ExportApplication():
            contacts = email.get_application_contacts(process)
        case _:
            raise ValueError(
                "Process must be an instance of ImportApplication / ExportApplication / AccessRequest"
            )

    for contact in contacts:
        send_notification(
            context["subject"],
            "email/base.html",
            context=context,
            recipients=utils.get_notification_emails(contact),
            cc_list=fir.email_cc_address_list,
            attachment_ids=attachment_ids,
        )


def send_further_information_request_withdrawal(
    process: Process, fir: FurtherInformationRequest
) -> None:
    subject = f"Withdrawn - {process.reference} Further Information Request"
    body = "The FIR request has been withdrawn by ILB."

    send_fir_to_contacts(process, fir, {"subject": subject, "body": body})


def further_information_responded(process: Process, fir: FurtherInformationRequest) -> None:
    subject = f"FIR Response - {process.reference} - {fir.request_subject}"
    fir_type = "access request" if isinstance(process, AccessRequest) else "case"

    send_notification(
        subject,
        "email/base.html",
        context={
            "subject": subject,
            "body": f"A FIR response has been submitted for {fir_type} {process.reference}.",
        },
        recipients=utils.get_notification_emails(fir.requested_by),
    )


@app.task(name="web.notify.notify.send_firearms_authority_expiry_notification")
def send_firearms_authority_expiry_notification() -> None:
    """Sends a notification to constabulary contacts verified firearms authority editors for verified firearms
    authorities that expire in 30 days"""

    logger.info("Running firearms authority expiry notification task")

    expiry_date = timezone.now().date() + dt.timedelta(days=30)
    expiry_date_str = expiry_date.strftime("%-d %B %Y")
    subject = f"Verified Firearms Authorities Expiring {expiry_date_str}"

    constabularies = Constabulary.objects.filter(
        firearmsauthority__end_date=expiry_date, is_active=True
    ).distinct()

    for constabulary in constabularies:
        importers = (
            Importer.objects.filter(
                firearms_authorities__issuing_constabulary=constabulary,
                firearms_authorities__end_date=expiry_date,
                is_active=True,
            )
            .annotate(
                authority_refs=StringAgg(
                    "firearms_authorities__reference",
                    delimiter=", ",
                    ordering="firearms_authorities__reference",
                )
            )
            .order_by("name")
        )
        recipient_users = constabulary_get_contacts(
            constabulary, perms=[Perms.obj.constabulary.verified_fa_authority_editor.codename]
        )

        for user in recipient_users:
            send_notification(
                subject,
                "email/import/authority_expiring.html",
                context={
                    "section_5": False,
                    "expiry_date": expiry_date_str,
                    "constabulary_name": constabulary.name,
                    "importers": importers,
                    "subject": subject,
                },
                recipients=utils.get_notification_emails(user),
            )

    logger.info(
        f"Firearms authority expiry notifications sent to {constabularies.count()} constabulary's contacts"
    )


@app.task(name="web.notify.notify.send_section_5_expiry_notification")
def send_section_5_expiry_notification() -> None:
    """Sends a notification to all verified section 5 authority editors for verified section 5 authorities
    that expire in 30 days"""

    logger.info("Running section 5 authority expiry notification task")

    expiry_date = timezone.now().date() + dt.timedelta(days=30)
    expiry_date_str = expiry_date.strftime("%-d %B %Y")
    subject = f"Verified Section 5 Authorities Expiring {expiry_date_str}"

    importers = (
        Importer.objects.filter(
            section5_authorities__end_date=expiry_date,
            is_active=True,
        )
        .annotate(
            authority_refs=StringAgg(
                "section5_authorities__reference",
                delimiter=", ",
                ordering="section5_authorities__reference",
            )
        )
        .order_by("name")
    )

    if not importers:
        return

    recipient_users = User.objects.filter(
        groups__permissions__codename=SysPerms.edit_section_5_firearm_authorities.codename
    )

    for user in recipient_users:
        send_notification(
            subject,
            "email/import/authority_expiring.html",
            context={
                "expiry_date": expiry_date_str,
                "section_5": True,
                "importers": importers,
                "subject": subject,
            },
            recipients=utils.get_notification_emails(user),
        )

    logger.info(
        f"Section 5 authority expiry notifications sent to {importers.count()} importers contacts"
    )


def authority_archived_notification(
    authority: FirearmsAuthority | Section5Authority,
    authority_type: Literal["Firearms", "Section 5"],
) -> None:
    """Sends a notification to all importer maintainers when a verified authority is archived"""

    archived_date = timezone.now().strftime("%-d %B %Y")
    subject = f"Importer {authority.importer.id} Verified {authority_type} Authority {authority.reference} Archived {archived_date}"

    recipient_users = User.objects.filter(groups__permissions__codename=SysPerms.ilb_admin.codename)

    for user in recipient_users:
        send_notification(
            subject,
            "email/import/authority_archived.html",
            context={
                "authority_type": authority_type,
                "authority": authority,
                "subject": subject,
            },
            recipients=utils.get_notification_emails(user),
        )


def send_constabulary_deactivated_firearms_notification(application: DFLApplication) -> None:
    subject = "Automatic Notification: Deactivated Firearm Licence Authorised"
    template = "email/import/constabulary_notification.html"
    context = {"subject": subject, "ilb_email": settings.ILB_CONTACT_EMAIL}

    html_message = utils.render_email(template, context)
    body = html2text.html2text(html_message)
    recipients = [application.constabulary.email]
    doc_pack = document_pack.pack_active_get(application)
    attachment_ids = tuple(doc_pack.document_references.values_list("document__id", flat=True))

    email.send_email.delay(
        subject, body, recipients, attachment_ids=attachment_ids, html_message=html_message
    )
