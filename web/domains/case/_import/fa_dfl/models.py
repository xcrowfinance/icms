from typing import TYPE_CHECKING, Literal, final

from django.db import models
from django.urls import reverse

from web.domains.case._import.fa.models import (
    SupplementaryInfoBase,
    SupplementaryReportBase,
    SupplementaryReportFirearmBase,
)
from web.domains.case._import.models import ChecklistBase, ImportApplication
from web.domains.constabulary.models import Constabulary
from web.domains.country.models import Country
from web.domains.file.models import File
from web.flow.models import ProcessTypes
from web.models.shared import FirearmCommodity, YesNoNAChoices

if TYPE_CHECKING:
    from django.db.models import QuerySet


class DFLGoodsCertificate(File):
    """Deactivated Firearms Licence Goods certificate"""

    goods_description = models.CharField(max_length=4096, verbose_name="Goods Description")

    deactivated_certificate_reference = models.CharField(
        max_length=50, verbose_name="Deactivated Certificate Reference"
    )

    issuing_country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name="Issuing Country",
        blank=False,
        null=False,
    )

    def __str__(self):
        dcf = self.deactivated_certificate_reference
        return f"DFLGoodsCertificate(id={self.pk}, deactivated_certificate_reference={dcf!r})"


@final
class DFLApplication(ImportApplication):
    """Firearms & Ammunition Deactivated Firearms Licence application"""

    PROCESS_TYPE = ProcessTypes.FA_DFL
    IS_FINAL = True

    deactivated_firearm = models.BooleanField(verbose_name="Deactivated Firearm", default=True)
    proof_checked = models.BooleanField(verbose_name="Proof Checked", default=False)

    # Goods section fields
    commodity_code = models.CharField(
        max_length=40,
        null=True,
        choices=FirearmCommodity.choices,
        verbose_name="Commodity Code",
        help_text=(
            "You must pick the commodity code group that applies to the items that you wish to"
            ' import. Please note that "ex Chapter 97" is only relevant to collectors pieces and'
            " items over 100 years old. Please contact HMRC classification advisory service,"
            " 01702 366077, if you are unsure of the correct code."
        ),
    )

    constabulary = models.ForeignKey(Constabulary, on_delete=models.PROTECT, null=True)
    goods_certificates = models.ManyToManyField(DFLGoodsCertificate, related_name="dfl_application")

    know_bought_from = models.BooleanField(
        blank=False,
        null=True,
        verbose_name="Do you know who you plan to buy/obtain these items from?",
    )

    def __str__(self):
        return f"DFLApplication(id={self.pk}, status={self.status!r}, is_active={self.is_active})"


class DFLChecklist(ChecklistBase):
    import_application = models.OneToOneField(
        DFLApplication, on_delete=models.PROTECT, related_name="checklist"
    )

    deactivation_certificate_attached = models.CharField(
        max_length=3,
        choices=YesNoNAChoices.choices,
        null=True,
        verbose_name="Deactivation certificate attached?",
    )

    deactivation_certificate_issued = models.CharField(
        max_length=3,
        choices=YesNoNAChoices.choices,
        null=True,
        verbose_name="Deactivation certificate issued by competent authority?",
    )


class DFLSupplementaryInfo(SupplementaryInfoBase):
    import_application = models.OneToOneField(
        DFLApplication, on_delete=models.CASCADE, related_name="supplementary_info"
    )


class DFLSupplementaryReport(SupplementaryReportBase):
    supplementary_info = models.ForeignKey(
        DFLSupplementaryInfo, related_name="reports", on_delete=models.CASCADE
    )

    def get_goods_certificates(self) -> "QuerySet[DFLGoodsCertificate]":
        return self.supplementary_info.import_application.goods_certificates.filter(is_active=True)

    def get_report_firearms(self) -> "QuerySet[DFLSupplementaryReportFirearm]":
        return self.firearms.all()

    def get_manual_add_firearm_url(self, goods_pk: int) -> str:
        return reverse(
            "import:fa-dfl:report-firearm-manual-add",
            kwargs={
                "application_pk": self.supplementary_info.import_application.pk,
                "goods_pk": goods_pk,
                "report_pk": self.pk,
            },
        )


class DFLSupplementaryReportFirearm(SupplementaryReportFirearmBase):
    report = models.ForeignKey(
        DFLSupplementaryReport, related_name="firearms", on_delete=models.CASCADE
    )

    goods_certificate = models.ForeignKey(
        DFLGoodsCertificate, related_name="supplementary_report_firearms", on_delete=models.CASCADE
    )

    def get_description(self) -> str:
        return self.goods_certificate.goods_description

    def get_manual_url(self, url_type: Literal["edit", "delete"]) -> str:
        return reverse(
            f"import:fa-dfl:report-firearm-manual-{url_type}",
            kwargs={
                "application_pk": self.report.supplementary_info.import_application.pk,
                "report_pk": self.report.pk,
                "report_firearm_pk": self.pk,
            },
        )
