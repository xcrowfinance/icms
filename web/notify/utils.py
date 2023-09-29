from collections.abc import Collection

from django.conf import settings
from django.template.loader import render_to_string

from web.models import Email, File, User
from web.sites import get_caseworker_site_domain
from web.utils.s3 import get_file_from_s3, get_s3_client


def get_user_emails_by_ids(user_ids: list[int]) -> list[str]:
    """Return a list emails for given users' ids"""
    return list(
        Email.objects.filter(user_id__in=user_ids)
        .filter(portal_notifications=True)
        .values_list("email", flat=True)
        .distinct()
        .order_by("email")
    )


def get_notification_emails(user: User) -> list[str]:
    """Returns user's personal and alternative email addresses
    with portal notifications enabled"""
    return get_user_emails_by_ids([user.id])


def render_email(template, context):
    """Adds shared variables into context and renders the email"""
    context = context or {}
    # TODO: ICMSLST-2313 Revisit (render_email used in 5 places)
    context["url"] = get_caseworker_site_domain()
    context["contact_email"] = settings.ILB_CONTACT_EMAIL
    context["contact_phone"] = settings.ILB_CONTACT_PHONE
    return render_to_string(template, context)


def get_attachments(file_ids: Collection[int]) -> Collection[tuple[str, bytes]]:
    if not file_ids:
        return []

    attachments = []
    files = File.objects.filter(pk__in=file_ids).values("path", "filename").order_by("pk")
    s3_client = get_s3_client()

    for f in files:
        file_content = get_file_from_s3(f["path"], client=s3_client)
        attachments.append((f["filename"], file_content))

    return attachments
