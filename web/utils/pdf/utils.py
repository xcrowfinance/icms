from typing import TYPE_CHECKING, Union

from django.conf import settings
from django.utils import timezone

from web.domains.case.services import document_pack
from web.domains.template.utils import get_cover_letter_content, get_letter_fragment
from web.types import DocumentTypes

if TYPE_CHECKING:
    from django.db.models import QuerySet

    from web.domains.case._import.fa.types import FaImportApplication
    from web.domains.case._import.fa_sil import models as sil_models
    from web.domains.case.types import ImpOrExp
    from web.models import (
        DFLApplication,
        ImportApplication,
        ImportApplicationLicence,
        OpenIndividualLicenceApplication,
    )

    SILGoods = Union[
        sil_models.SILGoodsSection1,
        sil_models.SILGoodsSection2,
        sil_models.SILGoodsSection5,
        sil_models.SILGoodsSection582Obsolete,  # /PS-IGNORE
        sil_models.SILGoodsSection582Other,  # /PS-IGNORE
    ]

    Context = dict[str, str | bool | list[str] | ImpOrExp]


def get_licence_context(
    application: "ImpOrExp", licence: "ImportApplicationLicence", doc_type: DocumentTypes
) -> "Context":
    return {
        "process": application,
        "issue_date": timezone.now().date().strftime("%d %B %Y"),
        "page_title": "Licence Preview",
        "preview_licence": doc_type == DocumentTypes.LICENCE_PREVIEW,
        "paper_licence_only": licence.issue_paper_licence_only or False,
    }


def _get_fa_licence_context(
    application: "FaImportApplication", licence: "ImportApplicationLicence", doc_type: DocumentTypes
) -> "Context":
    importer = application.importer
    office = application.importer_office
    endorsements = get_licence_endorsements(application)
    context = get_licence_context(application, licence, doc_type)

    return context | {
        "applicant_reference": application.applicant_reference,
        "importer_name": importer.display_name,
        "licence_start_date": _get_licence_start_date(licence),
        "licence_end_date": _get_licence_end_date(licence),
        "licence_number": _get_licence_number(application, doc_type),
        "eori_numbers": _get_importer_eori_numbers(application),
        "importer_address": office.address.split("\n"),
        "importer_postcode": office.postcode,
        "endorsements": endorsements,
    }


def get_fa_oil_licence_context(
    application: "OpenIndividualLicenceApplication",
    licence: "ImportApplicationLicence",
    doc_type: DocumentTypes,
) -> "Context":
    context = _get_fa_licence_context(application, licence, doc_type)

    return context | {
        "consignment_country": "Any Country",
        "origin_country": "Any Country",
        "goods_description": application.goods_description(),
    }


def get_fa_dfl_licence_context(
    application: "DFLApplication", licence: "ImportApplicationLicence", doc_type: DocumentTypes
) -> "Context":
    context = _get_fa_licence_context(application, licence, doc_type)

    return context | {
        "consignment_country": application.consignment_country.name,
        "origin_country": application.origin_country.name,
        "goods": _get_fa_dfl_goods(application),
    }


def get_fa_sil_licence_context(
    application: "sil_models.SILApplication",
    licence: "ImportApplicationLicence",
    doc_type: DocumentTypes,
) -> "Context":
    context = _get_fa_licence_context(application, licence, doc_type)
    markings_text = get_letter_fragment(application)

    return context | {
        "consignment_country": application.consignment_country.name,
        "origin_country": application.origin_country.name,
        "goods": _get_fa_sil_goods(application),
        "markings_text": markings_text,
    }


def get_cover_letter_context(
    application: "FaImportApplication", doc_type: DocumentTypes
) -> "Context":
    content = get_cover_letter_content(application, doc_type)
    preview = doc_type == DocumentTypes.COVER_LETTER_PREVIEW

    return {
        "content": content,
        "ilb_contact_email": settings.ILB_CONTACT_EMAIL,
        "issue_date": timezone.now().date().strftime("%d %B %Y"),
        "page_title": "Cover Letter Preview",
        "preview": preview,
        "process": application,
    }


# TODO: ICMSLST-1428 Revisit this - See nl2br
#       Add proper test for this function
def get_licence_endorsements(application: "ImpOrExp") -> list[str]:
    endorsements = [
        content.split("\r\n")
        for content in application.endorsements.values_list("content", flat=True)
    ]

    return endorsements


def _get_fa_dfl_goods(application: "DFLApplication") -> list[str]:
    return [
        g.goods_description
        for g in application.goods_certificates.all().order_by("created_datetime")
    ]


def _get_fa_sil_goods(application: "sil_models.SILApplication") -> list[tuple[str, int]]:
    """Return all related goods."""

    section_label_pairs = (
        ("goods_section1", "to which Section 1 of the Firearms Act 1968, as amended, applies."),
        ("goods_section2", "to which Section 2 of the Firearms Act 1968, as amended, applies."),
        (
            "goods_section5",
            "to which Section 5(1)(ac) of the Firearms Act 1968, as amended, applies.",
        ),
        (
            "goods_section582_others",
            "to which Section 58(2) of the Firearms Act 1968, as amended, applies.",
        ),
        (
            "goods_section582_obsoletes",
            "to which Section 58(2) of the Firearms Act 1968, as amended, applies.",
        ),
    )

    fa_sil_goods = []

    for goods_section, label_suffix in section_label_pairs:
        related_manager = getattr(application, goods_section)
        active_goods = related_manager.filter(is_active=True)
        fa_sil_goods.extend(get_fa_sil_goods_item(goods_section, active_goods, label_suffix))

    return fa_sil_goods


def get_fa_sil_goods_item(
    goods_section: str, active_goods: "QuerySet[SILGoods]", label_suffix: str
) -> list[tuple[str, int]]:
    if goods_section in ["goods_section1", "goods_section2", "goods_section582_others"]:
        return [(f"{g.description} {label_suffix}", g.quantity) for g in active_goods]

    elif goods_section == "goods_section5":
        goods = []

        for g in active_goods:
            quantity = "Unlimited" if g.unlimited_quantity else g.quantity
            goods.append((f"{g.description} {label_suffix}", quantity))

        return goods

    elif goods_section == "goods_section582_obsoletes":
        return [
            (
                f"{g.description} chambered in the obsolete calibre {g.obsolete_calibre} {label_suffix}",
                g.quantity,
            )
            for g in active_goods
        ]

    return []


def _get_licence_start_date(licence: "ImportApplicationLicence") -> str:
    if licence.licence_start_date:
        return licence.licence_start_date.strftime("%d %B %Y")

    return "Licence Start Date not set"


def _get_licence_end_date(licence: "ImportApplicationLicence") -> str:
    if licence.licence_end_date:
        return licence.licence_end_date.strftime("%d %B %Y")

    return "Licence End Date not set"


def _get_licence_number(application: "ImportApplication", doc_type: DocumentTypes) -> str:
    # TODO: ICMSLST-697 Revisit when signing the document (it may need its own context / template)
    if doc_type in (DocumentTypes.LICENCE_PRE_SIGN, DocumentTypes.LICENCE_SIGNED):
        doc_pack = document_pack.pack_latest_get(application)
        licence_doc = document_pack.doc_ref_licence_get(doc_pack)

        return licence_doc.reference

    return "[[Licence Number]]"


def _get_importer_eori_numbers(application: "FaImportApplication") -> list[str]:
    # TODO: ICMSLST-580 Revisit the EORI numbers that appear on a licence.
    # TODO: Check the Country of Consignment logic for other firearm licence types
    # TODO: If the applicant’s address has a BT (Belfast) post code AND the Country of Consignment is an EU country:

    importer = application.importer
    office = application.importer_office
    postcode = office.postcode
    is_northern_ireland = postcode and postcode.upper().startswith("BT") or False

    # Use override if set
    main_eori_num = office.eori_number or importer.eori_number

    # EORI numbers to return
    eori_numbers = [main_eori_num]

    if is_northern_ireland:
        eori_numbers.append(f"XI{main_eori_num[2:]}")

    return eori_numbers
