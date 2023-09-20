from urllib.parse import urljoin

from django.shortcuts import reverse
from django.templatetags.static import static

from web.domains.case.types import Authority, ImpOrExp
from web.models import FirearmsAuthority, Importer, Mailshot
from web.sites import get_caseworker_site_domain, get_importer_site_domain


def get_validate_digital_signatures_url(full_url: bool = False) -> str:
    url = static("web/docs/ValidateDigSigs.pdf")
    if full_url:
        return urljoin(get_importer_site_domain(), url)
    return url


def get_case_view_url(application: ImpOrExp, domain: str) -> str:
    url_kwargs = {"application_pk": application.pk}
    if application.is_import_application():
        url_kwargs["case_type"] = "import"
    else:
        url_kwargs["case_type"] = "export"
    return urljoin(domain, reverse("case:view", kwargs=url_kwargs))


def get_importer_view_url(importer: Importer, full_url: bool = False) -> str:
    url = reverse("importer-view", kwargs={"pk": importer.pk})
    if full_url:
        return urljoin(get_caseworker_site_domain(), url)
    return url


def get_authority_view_url(authority: Authority, full_url: bool = False) -> str:
    if authority.AUTHORITY_TYPE == FirearmsAuthority.AUTHORITY_TYPE:
        view_name = "importer-firearms-view"
    else:
        view_name = "importer-section5-view"

    url = reverse(view_name, kwargs={"pk": authority.pk})
    if full_url:
        return urljoin(get_caseworker_site_domain(), url)
    return url


def get_mailshot_detail_view_url(mailshot: Mailshot, domain: str) -> str:
    return urljoin(domain, reverse("mailshot-detail-received", kwargs={"mailshot_pk": mailshot.pk}))


def get_maintain_importers_view_url() -> str:
    return urljoin(get_caseworker_site_domain(), reverse("importer-list"))


def get_document_view_url(application: ImpOrExp, full_url: bool = False) -> str:
    url_kwargs = {"application_pk": application.pk}
    if application.is_import_application():
        url_kwargs["case_type"] = "import"
    else:
        url_kwargs["case_type"] = "export"
    url = reverse("case:applicant-case-history", kwargs=url_kwargs)
    if full_url:
        return urljoin(get_caseworker_site_domain(), url)
    return url
