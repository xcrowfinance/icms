from collections.abc import Generator
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import F, Value
from django.db.models.expressions import Window
from django.db.models.functions import Concat, RowNumber
from django.utils import timezone

from data_migration.models.base import MigrationBase
from data_migration.utils.format import split_address

EXCLUDE_DOMAIN = settings.DATA_MIGRATION_EMAIL_DOMAIN_EXCLUDE


class User(MigrationBase):
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    salt = models.CharField(max_length=16, null=True)
    encrypted_password = models.CharField(max_length=32, null=True)

    # Datetime TZ formatting looks for fields named _datetime
    last_login_datetime = models.DateTimeField(null=True)
    date_joined_datetime = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=20, null=True)
    preferred_first_name = models.CharField(max_length=4000, null=True)
    middle_initials = models.CharField(max_length=40, null=True)
    organisation = models.CharField(max_length=4000, null=True)
    department = models.CharField(max_length=4000, null=True)
    job_title = models.CharField(max_length=320, null=True)
    location_at_address = models.CharField(max_length=4000, null=True)
    work_address = models.CharField(max_length=300, null=True)
    date_of_birth = models.DateField(null=True)
    security_question = models.CharField(max_length=4000, null=True)
    security_answer = models.CharField(max_length=4000, null=True)
    share_contact_details = models.BooleanField(default=False)
    account_status = models.CharField(max_length=20)
    account_status_by = models.CharField(max_length=255, null=True)
    account_status_date = models.DateField(null=True)
    password_disposition = models.CharField(max_length=20, null=True)
    unsuccessful_login_attempts = models.PositiveSmallIntegerField(default=0)
    personal_email_xml = models.TextField(null=True)
    alternative_email_xml = models.TextField(null=True)
    telephone_xml = models.TextField(null=True)

    @classmethod
    def get_excludes(cls) -> list[str]:
        return super().get_excludes() + [
            "salt",
            "encrypted_password",
            "date_joined_datetime",
            "last_login_datetime",
            #
            # User fields removed in V2 model
            #
            "preferred_first_name",
            "middle_initials",
            "security_question",
            "security_answer",
            "share_contact_details",
            "account_status",
            "account_status_by",
            "account_status_date",
            "password_disposition",
            "unsuccessful_login_attempts",
        ]

    @classmethod
    def get_exclude_parameters(cls) -> dict[str, Any]:
        if EXCLUDE_DOMAIN:
            return {"username__iendswith": EXCLUDE_DOMAIN}
        return {}

    @classmethod
    def get_values_kwargs(cls) -> dict[str, Any]:
        return {
            "date_joined": F("date_joined_datetime"),
            "last_login": F("last_login_datetime"),
            "password": Concat(
                Value("fox_pbkdf2_sha1$10000$"),
                "id",
                Value(":"),
                "salt",
                Value("$"),
                "encrypted_password",
                output_field=models.CharField(),
            ),
        }

    @classmethod
    def get_source_data(cls) -> Generator:
        """Queries the model to get the queryset of data for the V2 import
        Filter out users whose username is not an email address
        """

        values = cls.get_values()
        values_kwargs = cls.get_values_kwargs()
        related = cls.get_related()
        return (
            cls.objects.select_related(*related)
            .exclude(pk=0)
            .exclude(**cls.get_exclude_parameters())
            .filter(username__contains="@")
            .order_by("pk")
            .annotate(icms_v1_user=Value(True))
            .values("icms_v1_user", *values, email=F("username"), **values_kwargs)
            .iterator(chunk_size=2000)
        )

    @classmethod
    def data_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        data = super().data_export(data)

        # This field in V2 defaults to True for new user records.
        # We don't want to show the welcome message to users from V1
        data["show_welcome_message"] = False

        return data


class PhoneNumber(MigrationBase):
    phone = models.CharField(max_length=60)
    type = models.CharField(max_length=30)
    comment = models.CharField(max_length=4000, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="phone_numbers")

    @classmethod
    def get_exclude_parameters(cls) -> dict[str, Any]:
        if EXCLUDE_DOMAIN:
            return {"user__username__iendswith": EXCLUDE_DOMAIN}
        return {}

    @classmethod
    def get_source_data(cls) -> Generator:
        """Queries the model to get the queryset of data for the V2 import"""

        values = cls.get_values()
        values_kwargs = cls.get_values_kwargs()
        related = cls.get_related()
        return (
            cls.objects.select_related(*related)
            .exclude(**cls.get_exclude_parameters())
            .filter(user__username__contains="@")
            .order_by("pk")
            .values(*values, **values_kwargs)
            .iterator(chunk_size=2000)
        )


class Email(MigrationBase):
    is_primary = models.BooleanField(blank=False, null=False, default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="emails")
    email = models.EmailField(max_length=254)
    type = models.CharField(max_length=30)
    portal_notifications = models.BooleanField(default=False)
    comment = models.CharField(max_length=4000, null=True)

    @classmethod
    def get_exclude_parameters(cls) -> dict[str, Any]:
        if EXCLUDE_DOMAIN:
            return {"user__username__iendswith": EXCLUDE_DOMAIN}
        return {}

    @classmethod
    def get_source_data(cls) -> Generator:
        """Queries the model to get the queryset of data for the V2 import"""

        values = cls.get_values()
        values_kwargs = cls.get_values_kwargs()
        related = cls.get_related()
        return (
            cls.objects.select_related(*related)
            .exclude(**cls.get_exclude_parameters())
            .filter(user__username__contains="@")
            .order_by("pk")
            .values(*values, **values_kwargs)
            .iterator(chunk_size=2000)
        )


class Importer(MigrationBase):
    is_active = models.BooleanField(default=True)
    type = models.CharField(max_length=20)
    name = models.TextField(null=True)
    registered_number = models.CharField(max_length=15, null=True)
    eori_number = models.CharField(max_length=20, null=True)
    region_origin = models.CharField(max_length=1, null=True)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="+",
    )
    comments = models.TextField(null=True)
    main_importer = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="+"
    )

    @classmethod
    def data_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        data = super().data_export(data)
        data["name"] = data["name"] or ""
        return data

    @classmethod
    def get_exclude_parameters(cls) -> dict[str, Any]:
        if EXCLUDE_DOMAIN:
            return {"user__username__iendswith": EXCLUDE_DOMAIN}
        return {}


class Exporter(MigrationBase):
    is_active = models.BooleanField(default=True)
    name = models.TextField()
    registered_number = models.CharField(max_length=15, null=True)
    comments = models.TextField(null=True)
    main_exporter = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, related_name="agents"
    )
    exclusive_correspondence = models.BooleanField(default=False)


class Office(MigrationBase):
    importer = models.ForeignKey(Importer, on_delete=models.CASCADE, null=True)
    exporter = models.ForeignKey(Exporter, on_delete=models.CASCADE, null=True)
    legacy_id = models.CharField(max_length=30, unique=True)
    is_active = models.BooleanField(default=True)
    postcode = models.CharField(max_length=30, null=True)
    address = models.CharField(max_length=4000, null=True)
    eori_number = models.CharField(max_length=20, null=True)
    address_entry_type = models.CharField(max_length=10, null=False, default="EMPTY")

    @classmethod
    def get_m2m_data(cls, target: models.Model) -> Generator:
        m2m_id = f"{target._meta.model_name}_id"

        if target._meta.model_name == "importer" and EXCLUDE_DOMAIN:
            extra_exclude = {"importer__user__username__endswith": EXCLUDE_DOMAIN}
        else:
            extra_exclude = {}

        return (
            cls.objects.exclude(**{f"{m2m_id}__isnull": True})
            .exclude(**extra_exclude)
            .annotate(row_number=Window(expression=RowNumber()))
            .values(
                "row_number",
                m2m_id,
                office_id=F("id"),
            )
            .iterator(chunk_size=2000)
        )

    @classmethod
    def get_exclude_parameters(cls) -> dict[str, Any]:
        if EXCLUDE_DOMAIN:
            return {"importer__user__username__iendswith": EXCLUDE_DOMAIN}
        return {}

    @classmethod
    def data_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        data = super().data_export(data)

        importer = data.pop("importer_id")
        exporter = data.pop("exporter_id")

        if importer:
            # Some extra data is in some postcode fields from a previous data migration
            # Postcodes can be a max of 8 characters
            postcode = data.pop("postcode")
            postcode = postcode and postcode.strip()[-8:]
            data["postcode"] = postcode

        elif exporter:
            # Exporters with long postcodes need postcode added to address field and postcode nullified
            if len(data["postcode"] or "") > 8:
                postcode = data.pop("postcode")
                data["address"] = data["address"] + "\n" + postcode

        # Addresses are split one field per line in V2
        address = data.pop("address")

        return data | split_address(address)

    @classmethod
    def m2m_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["id"] = data.pop("row_number")
        return data
