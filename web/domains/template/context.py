from typing import Protocol

from django.conf import settings
from django.db.models import F, QuerySet, Value

from web.domains.case.services import document_pack
from web.flow.models import ProcessTypes
from web.models import (
    AccessRequest,
    CFSProduct,
    CFSSchedule,
    ExportApplication,
    ImportApplication,
    Process,
)
from web.types import DocumentTypes
from web.utils import strip_spaces


def _get_selected_product_data(biocidal_schedules: QuerySet[CFSSchedule]) -> str:
    products = CFSProduct.objects.filter(schedule__in=biocidal_schedules)
    product_data = []

    for p in products:
        p_types = (str(pk) for pk in p.product_type_numbers.values_list("pk", flat=True))
        ingredient_list = p.active_ingredients.values_list("name", "cas_number")
        ingredients = (f"{name} ({cas})" for name, cas in ingredient_list)

        product = "\n".join(
            [
                f"Product: {p.product_name}",
                f"Product type numbers: {', '.join(p_types)}",
                f"Active ingredients (CAS numbers): f{', '.join(ingredients)}",
            ]
        )
        product_data.append(product)

    return "\n\n".join(product_data)


def _get_sil_goods_text(
    section: str | None, quantity: str | None, description: str, obsolete_calibre: str | None = None
) -> str:
    """Generates goods application text for SILApplication goods models"""

    if section:
        section_text = f" to which Section {section} of the Firearms Act 1968, as amended, applies."
    else:
        section_text = ""

    if obsolete_calibre:
        return f"{quantity} x {description} chambered in the obsolete calibre {obsolete_calibre}{section_text}"

    if quantity:
        return f"{quantity} x {description}{section_text}"

    return f"{description}{section_text}"


def _get_import_goods_description(app: ImportApplication) -> str:
    """Fetches the goods descriptions from the goods models for import applications"""

    match app.process_type:
        case ProcessTypes.FA_DFL:
            return "\n".join(app.goods_certificates.values_list("goods_description", flat=True))

        case ProcessTypes.FA_OIL:
            return (
                "Firearms, component parts thereof, or ammunition of any applicable"
                " commodity code, other than those falling under Section 5 of the Firearms Act 1968 as amended."
            )

        case ProcessTypes.FA_SIL:
            vals = ("quantity", "description")
            sec1 = app.goods_section1.values(*vals, section=Value("1"))
            sec2 = app.goods_section2.values(*vals, section=Value("2"))
            sec5 = app.goods_section5.values(*vals, section=F("subsection"))
            sec_obs = app.goods_section582_obsoletes.values(  # /PS-IGNORE
                "obsolete_calibre", *vals, section=Value("58(2)")  # /PS-IGNORE
            )
            sec_other = app.goods_section582_others.values(  # /PS-IGNORE
                *vals, section=Value("58(2)")  # /PS-IGNORE
            )
            sec_legacy_goods = app.goods_legacy.values("obsolete_calibre", *vals, section=Value(""))

            return "\n".join(
                [
                    _get_sil_goods_text(**values)
                    for sec in [
                        sec1,
                        sec2,
                        sec5,
                        sec_obs,
                        sec_other,
                        sec_legacy_goods,
                    ]
                    for values in sec
                ]
            )

        case ProcessTypes.SANCTIONS:
            return "\n".join(
                [
                    f"{str(quantity).rstrip('0').rstrip('.')} x {desc}"
                    for quantity, desc in app.sanctions_goods.values_list(
                        "quantity_amount", "goods_description"
                    ).order_by("pk")
                ]
            )

        case _:
            raise ValueError(
                f"GOODS_DESCRIPTION placeholder not supported for process type {app.process_type}"
            )


class TemplateContextProcessor(Protocol):
    def __init__(self, process: Process, *args, **kwargs):
        ...

    def __getitem__(self, item: str) -> str:
        ...


class CoverLetterTemplateContext:
    date_fmt = "%d %B %Y"

    valid_placeholders: list[str] = [
        "APPLICATION_SUBMITTED_DATE",
        "CONTACT_NAME",
        "COUNTRY_OF_CONSIGNMENT",
        "COUNTRY_OF_ORIGIN",
        "LICENCE_END_DATE",
        "LICENCE_NUMBER",
    ]

    def __init__(self, process: ImportApplication, document_type: DocumentTypes) -> None:
        self.application = process
        self.document_type = document_type

    def _placeholder(self, item: str) -> str:
        return f'<span class="placeholder">[[{item}]]</span>'

    def _context(self, item: str) -> str:
        match item:
            case "APPLICATION_SUBMITTED_DATE":
                return self.application.submit_datetime.strftime(self.date_fmt)
            case "CONTACT_NAME":
                return self.application.contact.full_name
            case "COUNTRY_OF_CONSIGNMENT":
                return self.application.consignment_country.name
            case "COUNTRY_OF_ORIGIN":
                return self.application.origin_country.name
            case _:
                raise ValueError(f"{item} is not a valid cover letter template context value")

    def _preview_context(self, item: str) -> str:
        match item:
            case "LICENCE_NUMBER":
                return self._placeholder(item)
            case "LICENCE_END_DATE":
                return self._placeholder(item)
        return self._context(item)

    def _full_context(self, item: str) -> str:
        licence = document_pack.pack_draft_get(self.application)

        match item:
            case "LICENCE_NUMBER":
                return document_pack.doc_ref_licence_get(licence).reference
            case "LICENCE_END_DATE":
                return licence.licence_end_date.strftime(self.date_fmt)
        return self._context(item)

    def __getitem__(self, item: str) -> str:
        match self.document_type:
            case DocumentTypes.COVER_LETTER_PREVIEW:
                return self._preview_context(item)
            case DocumentTypes.COVER_LETTER_PRE_SIGN:
                return self._full_context(item)
            case DocumentTypes.COVER_LETTER_SIGNED:
                return self._full_context(item)
            case _:
                raise ValueError(f"{self.document_type} is not a valid document type")


class EmailTemplateContext:
    def __init__(self, process: Process, current_user_name: str = "") -> None:
        self.process = process
        self.current_user_name = current_user_name

    def __getitem__(self, item: str) -> str:
        match self.process:
            case ImportApplication():
                return self._import_context(item)
            case ExportApplication():
                return self._export_context(item)
            case AccessRequest():
                return self._access_request_context(item)
            case _:
                raise ValueError(
                    "Process must be an instance of ImportApplication /"
                    " ExportApplication / AccessRequest"
                )

    def _application_context(self, item: str) -> str:
        match item:
            case "APPLICATION_TYPE":
                return self.process.PROCESS_TYPE.label
            case "CASE_OFFICER_EMAIL":
                return settings.ILB_CONTACT_EMAIL
            case "CASE_OFFICER_NAME":
                return self.process.case_owner.full_name
            case "CASE_OFFICER_PHONE":
                return settings.ILB_CONTACT_PHONE
            case "CASE_REFERENCE":
                return self.process.reference
            case "CONTACT_EMAIL":
                return self.process.contact.email
        return self._context(item)

    def _import_context(self, item: str) -> str:
        match item:
            case "GOODS_DESCRIPTION":
                return _get_import_goods_description(self.process)
            case "LICENCE_NUMBER":
                pack = document_pack.pack_active_get(self.process)
                return document_pack.doc_ref_licence_get(pack).reference
            case "IMPORTER_NAME":
                return self.process.importer.display_name
            case "IMPORTER_ADDRESS":
                return str(self.process.importer_office)
        return self._application_context(item)

    def _export_context(self, item: str) -> str:
        match item:
            case "CERT_COUNTRIES":
                return "\n".join(
                    self.process.countries.filter(is_active=True).values_list("name", flat=True)
                )
            case "CERTIFICATE_REFERENCES":
                pack = document_pack.pack_active_get(self.process)
                certificates = document_pack.doc_ref_certificates_all(pack)
                return ", ".join(certificates.values_list("reference", flat=True))
            case "EXPORTER_ADDRESS":
                return str(self.process.exporter_office)
            case "EXPORTER_NAME":
                return str(self.process.exporter)

        match self.process.process_type:
            case ProcessTypes.GMP:
                return self._gmp_app_context(item)
            case ProcessTypes.CFS:
                return self._cfs_app_context(item)

        return self._application_context(item)

    def _gmp_app_context(self, item: str) -> str:
        match item:
            case "MANUFACTURER_NAME":
                return self.process.manufacturer_name
            case "MANUFACTURER_ADDRESS":
                return self.process.manufacturer_address
            case "MANUFACTURER_POSTCODE":
                return self.process.manufacturer_postcode
            case "RESPONSIBLE_PERSON_ADDRESS":
                return self.process.responsible_person_address
            case "RESPONSIBLE_PERSON_NAME":
                return self.process.responsible_person_name
            case "RESPONSIBLE_PERSON_POSTCODE":
                return self.process.responsible_person_postcode
            case "BRAND_NAMES":
                # No longer a list of values
                return self.process.brand_name

        return self._application_context(item)

    def _cfs_app_context(self, item: str) -> str:
        match item:
            case "SELECTED_PRODUCTS":
                return _get_selected_product_data(
                    self.process.schedules.filter(legislations__is_biocidal=True)
                )

        return self._application_context(item)

    def _access_request_context(self, item: str) -> str:
        match item:
            case "CURRENT_USER_NAME":
                return self.current_user_name
            case "REQUESTER_NAME":
                return self.process.submitted_by.full_name
            case "REQUEST_REFERENCE":
                return self.process.reference

        return self._context(item)

    def _context(self, item: str) -> str:
        match item:
            case _:
                raise ValueError(f"{item} is not a valid email template context value")


class ScheduleParagraphContext:
    def __init__(self, schedule: CFSSchedule) -> None:
        self.schedule = schedule

    def __getitem__(self, item: str) -> str:
        match item:
            case "EXPORTER_NAME":
                return self.schedule.application.exporter.name.upper()
            case "EXPORTER_ADDRESS_FLAT":
                return strip_spaces(str(self.schedule.application.exporter_office).upper())
            case "COUNTRY_OF_MANUFACTURE":
                return self.schedule.country_of_manufacture.name
            case "MANUFACTURED_AT_NAME":
                return self.schedule.manufacturer_name
            case "MANUFACTURED_AT_ADDRESS_FLAT":
                return strip_spaces(
                    self.schedule.manufacturer_address, self.schedule.manufacturer_postcode
                )
            case _:
                raise ValueError(f"{item} is not a valid schedule paragraph context value")
