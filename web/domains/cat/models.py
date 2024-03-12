from typing import TYPE_CHECKING

from django.conf import settings
from django.db import models

from web.domains.case.export.models import (
    CertificateOfGoodManufacturingPracticeApplicationABC,
    CertificateOfManufactureApplicationABC,
    ExportApplicationABC,
)
from web.models import ExportApplicationType
from web.types import TypedTextChoices

if TYPE_CHECKING:
    from web.models import User


class CertificateApplicationTemplate(models.Model):
    class SharingStatuses(TypedTextChoices):
        PRIVATE = ("private", "Private (do not share)")
        VIEW = ("view", "Share (view only)")
        EDIT = ("edit", "Share (allow edit)")

    name = models.CharField(verbose_name="Template Name", max_length=70)

    description = models.CharField(verbose_name="Template Description", max_length=500)

    application_type = models.CharField(
        verbose_name="Application Type",
        max_length=3,
        choices=ExportApplicationType.Types.choices,
        help_text=(
            "DIT does not issue Certificates of Free Sale for food, food supplements, pesticides"
            " and CE marked medical devices. Certificates of Manufacture are applicable only to"
            " pesticides that are for export only and not on free sale on the domestic market."
        ),
    )

    sharing = models.CharField(
        max_length=7,
        choices=SharingStatuses.choices,
        help_text=(
            "Whether or not other contacts of exporters/agents you are a contact of should"
            " be able view and create applications using this template, and if they can edit it."
        ),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    def user_can_view(self, user: "User") -> bool:
        # A template may have sensitive information so we check if the user
        # should be allowed to view it (use it to create an application).
        return user == self.owner

    def user_can_edit(self, user: "User") -> bool:
        # Whether the user can edit the template itself.
        return user == self.owner


class CertificateOfManufactureApplicationTemplate(  # type: ignore[misc]
    ExportApplicationABC, CertificateOfManufactureApplicationABC
):
    template = models.OneToOneField(
        "web.CertificateApplicationTemplate", on_delete=models.CASCADE, related_name="com_template"
    )


class CertificateOfFreeSaleApplicationTemplate: ...  # noqa: E701


class CertificateOfGoodManufacturingPracticeApplicationTemplate(  # type: ignore[misc]
    ExportApplicationABC, CertificateOfGoodManufacturingPracticeApplicationABC
):
    template = models.OneToOneField(
        "web.CertificateApplicationTemplate", on_delete=models.CASCADE, related_name="gmp_template"
    )
