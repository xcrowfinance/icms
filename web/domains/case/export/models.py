from django.db import models

from web.domains.case.fir.models import FurtherInformationRequest
from web.domains.case.models import (
    ApplicationBase,
    CaseEmail,
    CaseNote,
    UpdateRequest,
    VariationRequest,
)
from web.domains.country.models import Country, CountryGroup
from web.domains.exporter.models import Exporter
from web.domains.file.models import File
from web.domains.legislation.models import ProductLegislation
from web.domains.office.models import Office
from web.domains.user.models import User
from web.models.shared import AddressEntryType, YesNoChoices


class ExportApplicationType(models.Model):
    class Types(models.TextChoices):
        FREE_SALE = ("CFS", "Certificate of Free Sale")
        MANUFACTURE = ("COM", "Certificate of Manufacture")
        GMP = ("GMP", "Certificate of Good Manufacturing Practice")

    class ProcessTypes(models.TextChoices):
        COM = ("CertificateOfManufactureApplication", "Certificate of Manufacture")
        CFS = ("CertificateOfFreeSaleApplication", "Certificate of Free Sale")
        GMP = (
            "CertificateofGoodManufacturingPractice",
            "Certificate of Good Manufacturing Practice",
        )

    is_active = models.BooleanField(blank=False, null=False, default=True)
    type_code = models.CharField(
        max_length=30, blank=False, null=False, unique=True, choices=Types.choices
    )
    type = models.CharField(max_length=70, blank=False, null=False)
    allow_multiple_products = models.BooleanField(blank=False, null=False)
    generate_cover_letter = models.BooleanField(blank=False, null=False)
    allow_hse_authorization = models.BooleanField(blank=False, null=False)
    country_group = models.ForeignKey(
        CountryGroup, on_delete=models.PROTECT, blank=False, null=False
    )
    country_group_for_manufacture = models.ForeignKey(
        CountryGroup,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="manufacture_export_application_types",
    )

    def __str__(self):
        return f"{self.type}"

    class Meta:
        ordering = ("type",)


class ExportApplication(ApplicationBase):
    application_type = models.ForeignKey(
        ExportApplicationType, on_delete=models.PROTECT, blank=False, null=False
    )

    last_update_datetime = models.DateTimeField(blank=False, null=False, auto_now=True)

    last_updated_by = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=False, null=False, related_name="updated_export_cases"
    )

    variation_requests = models.ManyToManyField(VariationRequest)
    variation_no = models.IntegerField(blank=False, null=False, default=0)
    case_notes = models.ManyToManyField(CaseNote)
    further_information_requests = models.ManyToManyField(FurtherInformationRequest)
    update_requests = models.ManyToManyField(UpdateRequest)
    case_emails = models.ManyToManyField(CaseEmail, related_name="+")

    submitted_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="submitted_export_application",
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="created_export_applications",
    )

    exporter = models.ForeignKey(
        Exporter,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="export_applications",
    )

    exporter_office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        blank=False,
        null=True,
        related_name="office_export_applications",
    )

    contact = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        null=True,
        related_name="contact_export_applications",
        help_text=(
            "Select the main point of contact for the case. This will usually"
            " be the person who created the application."
        ),
    )

    countries = models.ManyToManyField(
        Country,
        help_text=(
            "A certificate will be created for each country selected. You may"
            " select up to 40 countries. You cannot select the same country"
            " twice, you must submit a new application."
        ),
    )

    agent = models.ForeignKey(
        Exporter,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="agent_export_applications",
    )
    agent_office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="agent_office_export_applications",
    )
    case_owner = models.ForeignKey(
        User, on_delete=models.PROTECT, blank=True, null=True, related_name="+"
    )

    def is_import_application(self) -> bool:
        return False

    def get_edit_view_name(self) -> str:
        if self.process_type == ExportApplicationType.ProcessTypes.COM:
            return "export:com-edit"
        if self.process_type == ExportApplicationType.ProcessTypes.CFS:
            return "export:cfs-edit"
        if self.process_type == ExportApplicationType.ProcessTypes.GMP:
            return "export:gmp-edit"
        else:
            raise NotImplementedError(f"Unknown process_type {self.process_type}")

    def get_submit_view_name(self) -> str:
        if self.process_type == ExportApplicationType.ProcessTypes.COM:
            return "export:com-submit"
        if self.process_type == ExportApplicationType.ProcessTypes.CFS:
            return "export:cfs-submit"
        if self.process_type == ExportApplicationType.ProcessTypes.GMP:
            return "export:gmp-submit"
        else:
            raise NotImplementedError(f"Unknown process_type {self.process_type}")

    def user_is_contact_of_org(self, user: User) -> bool:
        return user.has_perm("web.is_contact_of_exporter", self.exporter)

    def user_is_agent_of_org(self, user: User) -> bool:
        return user.has_perm("web.is_agent_of_exporter", self.exporter)

    def get_workbasket_subject(self) -> str:
        return "\n".join(
            [
                "Certificate Application",
                ExportApplicationType.ProcessTypes(self.process_type).label,
            ]
        )


class CertificateOfManufactureApplication(ExportApplication):
    PROCESS_TYPE = ExportApplicationType.ProcessTypes.COM

    is_pesticide_on_free_sale_uk = models.BooleanField(null=True)
    is_manufacturer = models.BooleanField(null=True)

    product_name = models.CharField(max_length=1000, blank=False)
    chemical_name = models.CharField(max_length=500, blank=False)
    manufacturing_process = models.TextField(max_length=4000, blank=False)


class CertificateOfFreeSaleApplication(ExportApplication):
    PROCESS_TYPE = ExportApplicationType.ProcessTypes.CFS

    schedules = models.ManyToManyField("CFSSchedule")


class CFSSchedule(models.Model):
    class ExporterStatus(models.TextChoices):
        IS_MANUFACTURER = ("MANUFACTURER", "I am the manufacturer")
        IS_NOT_MANUFACTURER = ("NOT_MANUFACTURER", "I am not the manufacturer")

    class ProductEligibility(models.TextChoices):
        SOLD_ON_UK_MARKET = (
            "SOLD_ON_UK_MARKET",
            "The products are currently sold on the UK market",
        )
        MEET_UK_PRODUCT_SAFETY = (
            "MEET_UK_PRODUCT_SAFETY",
            "The products meet the product safety requirements to be sold on the UK market",
        )

    exporter_status = models.CharField(
        null=True, verbose_name="Exporter Status", choices=ExporterStatus.choices, max_length=16
    )

    brand_name_holder = models.CharField(
        max_length=3,
        choices=YesNoChoices.choices,
        null=True,
        verbose_name="Are you the Brand name holder?",
    )

    legislations = models.ManyToManyField(
        ProductLegislation,
        verbose_name="Legislation",
        help_text=(
            "Enter legislation relevant to the products on this schedule. A"
            " maximum of 3 pieces of legislation may be added per schedule. If"
            " you cannot find relevant legislation, please contact DIT,"
            " enquiries.ilb@trade.gsi.gov.uk, to request to have it added."
        ),
    )

    product_eligibility = models.CharField(
        null=True,
        verbose_name="Product Eligibility",
        max_length=22,
        choices=ProductEligibility.choices,
        help_text=(
            "If your products are currently for export only, you MUST select"
            f" {ProductEligibility.MEET_UK_PRODUCT_SAFETY.label}"  # type: ignore[attr-defined]
        ),
    )

    goods_placed_on_uk_market = models.CharField(
        max_length=3,
        choices=YesNoChoices.choices,
        null=True,
        verbose_name="Have you placed the goods on the UK market or intend to place on UK market in future?",
    )

    goods_export_only = models.CharField(
        max_length=3,
        choices=YesNoChoices.choices,
        null=True,
        verbose_name="Are these goods for export only and will never be placed by you on the UK market?",
    )

    any_raw_materials = models.CharField(
        max_length=3,
        choices=YesNoChoices.choices,
        null=True,
        verbose_name="Are any of the products raw materials?",
        help_text="Only choose 'Yes' if the product is a material used in the manufacture of a finished product.",
    )

    final_product_end_use = models.CharField(null=True, blank=True, max_length=4000)

    country_of_manufacture = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        null=True,
        related_name="+",
        verbose_name="Country Of Manufacture",
        help_text="You can only list one country. Add another schedule if product information differs.",
    )

    schedule_statements = models.BooleanField(
        default=False,
        verbose_name="Schedule Statements",
        help_text="Select if applicable",
    )

    # "Manufactured at" section fields
    manufacturer_name = models.CharField(max_length=200, verbose_name="Name", null=True)

    manufacturer_address_entry_type = models.CharField(
        max_length=10,
        choices=AddressEntryType.choices,
        verbose_name="Address Type",
        default=AddressEntryType.MANUAL,
    )

    manufacturer_postcode = models.CharField(
        max_length=30, verbose_name="Postcode", null=True, blank=True
    )

    manufacturer_address = models.CharField(
        max_length=4000, verbose_name="Address", null=True, blank=True
    )

    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=False,
        null=False,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_biocidal(self) -> bool:
        return self.legislations.filter(is_biocidal=True).exists()


class CFSProduct(models.Model):
    product_name = models.CharField(max_length=1000)
    schedule = models.ForeignKey(CFSSchedule, related_name="products", on_delete=models.CASCADE)


class CFSProductType(models.Model):
    product_type_number = models.IntegerField(choices=[(i, i) for i in range(1, 23)])
    product = models.ForeignKey(
        CFSProduct, related_name="product_type_numbers", on_delete=models.CASCADE
    )


class CFSProductActiveIngredient(models.Model):
    name = models.CharField(max_length=500)
    cas_number = models.CharField(max_length=50, verbose_name="CAS Number")
    product = models.ForeignKey(
        CFSProduct, related_name="active_ingredients", on_delete=models.CASCADE
    )


class CertificateOfGoodManufacturingPracticeApplication(ExportApplication):
    PROCESS_TYPE = ExportApplicationType.ProcessTypes.GMP

    class CertificateTypes(models.TextChoices):
        ISO_22716 = ("ISO_22716", "ISO 22716")
        BRC_GSOCP = ("BRC_GSOCP", "BRC Global Standard for Consumer Products")

    class CountryType(models.TextChoices):
        GB = ("GB", "Great Britain")
        NIR = ("NIR", "Northern Ireland")

    # Responsible person fields
    is_responsible_person = models.CharField(
        max_length=3,
        choices=YesNoChoices.choices,
        null=True,
        default=None,
        verbose_name="Are you the responsible person as defined by Cosmetic Products Legislation as applicable in GB or NI?",
    )

    responsible_person_name = models.CharField(max_length=200, verbose_name="Name", null=True)

    responsible_person_address_entry_type = models.CharField(
        max_length=10,
        choices=AddressEntryType.choices,
        verbose_name="Address Type",
        default=AddressEntryType.MANUAL,
    )

    responsible_person_postcode = models.CharField(
        max_length=30,
        verbose_name="Postcode",
        null=True,
    )

    responsible_person_address = models.CharField(
        max_length=4000,
        verbose_name="Address",
        null=True,
    )

    responsible_person_country = models.CharField(
        max_length=3,
        choices=CountryType.choices,
        verbose_name="Country of Responsible Person",
        default=None,
        null=True,
    )

    # Manufacturer fields
    is_manufacturer = models.CharField(
        max_length=3,
        choices=YesNoChoices.choices,
        null=True,
        default=None,
        verbose_name="Are you the manufacturer of the cosmetic products?",
    )

    manufacturer_name = models.CharField(max_length=200, verbose_name="Name", null=True)

    manufacturer_address_entry_type = models.CharField(
        max_length=10,
        choices=AddressEntryType.choices,
        verbose_name="Address Type",
        default=AddressEntryType.MANUAL,
    )

    manufacturer_postcode = models.CharField(
        max_length=30,
        verbose_name="Postcode",
        null=True,
    )

    manufacturer_address = models.CharField(
        max_length=4000,
        verbose_name="Address",
        null=True,
    )

    manufacturer_country = models.CharField(
        max_length=3,
        choices=CountryType.choices,
        verbose_name="Country of Manufacture",
        null=True,
        default=None,
    )

    # Manufacturing certificates fields
    gmp_certificate_issued = models.CharField(
        max_length=10,
        null=True,
        choices=CertificateTypes.choices,
        verbose_name=(
            "Which valid certificate of Good Manufacturing Practice (GMP) has"
            " your cosmetics manufacturer been issued with?"
        ),
        default=None,
    )

    auditor_accredited = models.CharField(
        max_length=3,
        null=True,
        choices=YesNoChoices.choices,
        verbose_name=(
            "Is the auditor or auditing body who inspected and certified the"
            " manufacturing facility accredited according to ISO 17021 by a"
            " national accreditation body which is a member of the"
            " International Accreditation Forum?"
        ),
        default=None,
    )

    auditor_certified = models.CharField(
        max_length=3,
        null=True,
        choices=YesNoChoices.choices,
        verbose_name=(
            "Is the auditor or auditing body who inspected and certified the"
            " manufacturing facility accredited according to ISO 17065 by a"
            " national accreditation body which is a member of the"
            " International Accreditation Forum?"
        ),
        default=None,
    )

    supporting_documents = models.ManyToManyField("GMPFile")


class GMPFile(File):
    class Type(models.TextChoices):
        # ISO_22716 file types
        ISO_22716 = ("ISO_22716", "ISO 22716")
        ISO_17021 = ("ISO_17021", "ISO 17021")
        ISO_17065 = ("ISO_17065", "ISO 17065")

        # BRC Global Standard for Consumer Products file types
        BRC_GSOCP = ("BRC_GSOCP", "BRC Global Standard for Consumer Products")

    file_type = models.CharField(max_length=10, choices=Type.choices)
