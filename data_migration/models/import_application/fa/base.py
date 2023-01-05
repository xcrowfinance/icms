from collections.abc import Generator
from typing import Any

from django.db import models
from django.db.models import F, OuterRef, Q, Subquery

from data_migration import queries
from data_migration.models.base import MigrationBase
from data_migration.models.file import File, FileTarget
from data_migration.models.reference import CommodityGroup
from data_migration.models.user import User

from ..import_application import ImportApplication, ImportApplicationBase


class FirearmBase(ImportApplicationBase):
    class Meta:
        abstract = True

    know_bought_from = models.BooleanField(null=True)
    commodity_group = models.ForeignKey(CommodityGroup, on_delete=models.SET_NULL, null=True)
    commodities_xml = models.TextField(null=True)
    user_import_certs_xml = models.TextField(null=True)
    fa_authorities_xml = models.TextField(null=True)
    bought_from_details_xml = models.TextField(null=True)
    fa_goods_certs_xml = models.TextField(null=True)

    @classmethod
    def data_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        data = super().data_export(data)
        data["commodity_code"] = data.pop("commodity_group__group_name")
        return data

    @classmethod
    def get_excludes(cls) -> list[str]:
        return super().get_excludes() + ["commodity_group_id"]

    @classmethod
    def get_includes(cls) -> list[str]:
        return super().get_includes() + ["commodity_group__group_name"]


class UserImportCertificate(MigrationBase):
    target = models.ForeignKey(FileTarget, on_delete=models.CASCADE)
    import_application = models.ForeignKey(ImportApplication, on_delete=models.CASCADE)
    reference = models.CharField(max_length=200, null=True)
    certificate_type = models.CharField(max_length=200)
    constabulary = models.ForeignKey(
        "data_migration.Constabulary", on_delete=models.PROTECT, null=True
    )
    date_issued = models.DateField(null=True)
    expiry_date = models.DateField(null=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    @classmethod
    def data_export(cls, data: dict[str, Any]) -> dict[str, Any]:

        # Remove id and set file_ptr_id because V2 inherits from File model
        data.pop("id")

        # This is a M2M field in V2
        data.pop("import_application_id")

        # Set the updated_datetime to the created_datetime of the file or the autogenerated updated_datetime
        data["updated_datetime"] = data.pop("created_datetime") or data["updated_datetime"]
        return data

    @classmethod
    def get_excludes(cls) -> list[str]:
        return super().get_excludes() + ["target_id"]

    @classmethod
    def m2m_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        return data

    @classmethod
    def get_source_data(cls) -> Generator:
        """Queries the model to get the queryset of data for the V2 import"""

        values = cls.get_values() + ["file_ptr_id", "created_datetime"]
        sub_query = File.objects.filter(target_id=OuterRef("target_id"))

        # Exclude records with no file or unsubmitted applications where reference is null
        exclude_query = Q(file_ptr_id__isnull=True) | Q(
            Q(import_application__submit_datetime__isnull=True) & Q(reference__isnull=True)
        )

        return (
            cls.objects.select_related("target")
            .prefetch_related("target__files")
            .filter(constabulary__isnull=False)
            .annotate(
                file_ptr_id=Subquery(sub_query.values("pk")[:1]),
                created_datetime=Subquery(sub_query.values("created_datetime")[:1]),
            )
            .exclude(exclude_query)
            .values(*values)
            .iterator(chunk_size=2000)
        )

    @classmethod
    def get_m2m_data(cls, target: models.Model) -> Generator:
        sub_query = File.objects.filter(target_id=OuterRef("target_id"))
        m2m_id = f"{target._meta.model_name}_id"

        return (
            cls.objects.select_related("target")
            .prefetch_related("target__files")
            .filter(
                import_application__ima__process_type=target.PROCESS_TYPE,
                constabulary__isnull=False,
            )
            .exclude(import_application__submit_datetime__isnull=True, reference__isnull=True)
            .annotate(
                userimportcertificate_id=Subquery(sub_query.values("pk")[:1]),
                **{m2m_id: F("import_application_id")},
            )
            .exclude(userimportcertificate_id__isnull=True)
            .values("userimportcertificate_id", "id", m2m_id)
            .iterator(chunk_size=2000)
        )


class ImportContact(MigrationBase):
    UPDATE_TIMESTAMP_QUERY = queries.import_contact_timestamp_update

    import_application = models.ForeignKey(ImportApplication, on_delete=models.PROTECT)
    legacy_id = models.IntegerField()
    entity = models.CharField(max_length=20)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200, null=True)
    registration_number = models.CharField(max_length=200, null=True)
    street = models.CharField(max_length=200)
    city = models.CharField(max_length=200)
    postcode = models.CharField(max_length=200, null=True)
    region = models.CharField(max_length=200, null=True)
    country = models.ForeignKey(
        "data_migration.Country", on_delete=models.PROTECT, related_name="+"
    )
    dealer = models.CharField(max_length=10, null=True)
    created_datetime = models.DateTimeField()
    updated_datetime = models.DateTimeField(auto_now=True)


class SupplementaryInfoBase(MigrationBase):
    class Meta:
        abstract = True

    is_complete = models.BooleanField(default=False)
    completed_datetime = models.DateTimeField(null=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    no_report_reason = models.CharField(
        max_length=4000,
        null=True,
    )
    supplementary_report_xml = models.TextField(null=True)

    @classmethod
    def get_excludes(cls):
        return super().get_excludes() + ["imad_id"]

    @classmethod
    def get_includes(cls):
        return ["imad__id"]

    @classmethod
    def get_related(cls) -> list[str]:
        return ["imad"]

    @classmethod
    def data_export(cls, data: dict[str, Any]) -> dict[str, Any]:
        data["import_application_id"] = data.pop("imad__id")
        return data


class SupplementaryReportBase(MigrationBase):
    class Meta:
        abstract = True

    transport = models.CharField(max_length=4, null=True)
    date_received = models.DateField(null=True)
    bought_from_legacy_id = models.IntegerField(null=True)
    created = models.DateTimeField(auto_now=True)
    report_firearms_xml = models.TextField(null=True)

    @classmethod
    def get_excludes(cls) -> list[str]:
        return super().get_excludes() + ["bought_from_legacy_id"]

    @classmethod
    def get_source_data(cls) -> Generator:
        values = cls.get_values()
        values.append("bought_from_id")

        # Define an extra subquery to retrieve the ImportContact pk for the bought_from fk
        # In V1 the contact is linked by the "REPORT_SELLER_HOLDER" (bought_from_legacy_id) field
        # This id in V1 is only unique per application and not per import contact
        # We create a unique ID for the contact when extracting from V1 and link the fk here

        sub_query = ImportContact.objects.filter(
            import_application_id=models.OuterRef("supplementary_info__imad__pk"),
            legacy_id=models.OuterRef("bought_from_legacy_id"),
        )

        return (
            cls.objects.select_related("supplementary_info__imad")
            .annotate(bought_from_id=models.Subquery(sub_query.values("pk")[:1]))
            .values(*values)
            .iterator(chunk_size=2000)
        )


class SupplementaryReportFirearmBase(MigrationBase):
    class Meta:
        abstract = True

    serial_number = models.CharField(max_length=400, null=True)
    calibre = models.CharField(max_length=400, null=True)
    model = models.CharField(max_length=400, null=True)
    proofing = models.CharField(max_length=3, null=True, default=None)
    is_manual = models.BooleanField(default=False)
    is_upload = models.BooleanField(default=False)
    is_no_firearm = models.BooleanField(default=False)
    goods_certificate_legacy_id = models.PositiveIntegerField(null=True)

    @classmethod
    def get_excludes(cls) -> list[str]:
        return super().get_excludes() + ["goods_certificate_legacy_id"]
