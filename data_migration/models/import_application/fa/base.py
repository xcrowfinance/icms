from typing import Any, Generator, Optional, Tuple

from django.db import models
from django.db.models import OuterRef, Q, Subquery
from lxml import etree

from data_migration.models.base import MigrationBase
from data_migration.models.file import File, FileTarget
from data_migration.models.reference import CommodityGroup
from data_migration.models.user import User
from data_migration.utils.format import (
    date_or_none,
    get_xml_val,
    str_to_yes_no,
    xml_str_or_none,
)

from ..import_application import ImportApplication, ImportApplicationBase

FA_TYPE_CODES = {
    "DEACTIVATED": "deactivated",
    "RFD": "registered",
    # "SHOTGUN": "shotgun", TODO ICMSLST-1519 correct the key to match V1
    # "FA": "firearms",  TODO ICMSLST-1519 correct the key to match V1
}


class FirearmBase(ImportApplicationBase):
    class Meta:
        abstract = True

    know_bought_from = models.BooleanField(null=True)
    commodity_group = models.ForeignKey(CommodityGroup, on_delete=models.SET_NULL, null=True)
    commodities_xml = models.TextField(null=True)
    fa_certs_xml = models.TextField(null=True)
    fa_authorities_xml = models.TextField(null=True)
    bought_from_details_xml = models.TextField(null=True)

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
        return {
            "id": data["id"],
            "userimportcertificate_id": data["file_ptr_id"],
            "openindividuallicenceapplication_id": data["import_application_id"],
        }

    @classmethod
    def get_source_data(cls) -> Generator:
        """Queries the model to get the queryset of data for the V2 import"""

        values = cls.get_values() + ["file_ptr_id", "created_datetime"]
        sub_query = File.objects.filter(target_id=OuterRef("target_id"))

        # Exclude unsubmitted applications where reference, constabulary or expiry_date are null
        exclude_query = Q(import_application__submit_datetime__isnull=True) & Q(
            Q(reference__isnull=True) | Q(constabulary__isnull=True) | Q(expiry_date__isnull=True)
        )

        return (
            cls.objects.select_related("target")
            .prefetch_related("target__files")
            .annotate(
                file_ptr_id=Subquery(sub_query.values("pk")[:1]),
                created_datetime=Subquery(sub_query.values("created_datetime")[:1]),
            )
            .exclude(file_ptr_id__isnull=True)
            .exclude(exclude_query)
            .values(*values)
            .iterator()
        )

    @classmethod
    def parse_xml(cls, batch: list[Tuple[int, str]]) -> list[models.Model]:
        """Example XML

        <FIREARMS_CERTIFICATE_LIST>
          <FIREARMS_CERTIFICATE />
        </FIREARMS_CERTIFICATE_LIST>
        """
        model_list = []
        for parent_pk, xml_str in batch:
            xml_tree = etree.fromstring(xml_str)
            xml_list = xml_tree.xpath("FIREARMS_CERTIFICATE")
            for xml in xml_list:
                obj = cls.parse_xml_fields(parent_pk, xml)

                if obj:
                    model_list.append(obj)
        return model_list

    @classmethod
    def parse_xml_fields(
        cls, parent_pk: int, xml: etree.ElementTree
    ) -> Optional["UserImportCertificate"]:
        """Example XML structure

        <FIREARMS_CERTIFICATE>
          <TARGET_ID />
          <CERTIFICATE_REF />
          <CERTIFICATE_TYPE />
          <CONSTABULARY />
          <DATE_ISSUED />
          <EXPIRY_DATE />
          <ISSUING_COUNTRY />
        </FIREARMS_CERTIFICATE>
        """
        target_id = get_xml_val(xml, "./TARGET_ID/text()")
        certificate_type = get_xml_val(xml, "./CERTIFICATE_TYPE/text()")

        if not target_id or not certificate_type:
            # There needs to be an file and certificate_type associated with the data
            return None

        reference = get_xml_val(xml, "./CERTIFICATE_REF/text()")
        constabulary_id = get_xml_val(xml, "./CONSTABULARY/text()")
        date_issued = get_xml_val(xml, "./DATE_ISSUED/text()")
        expiry_date = get_xml_val(xml, "./EXPIRY_DATE/text()")

        return cls(
            **{
                "import_application_id": parent_pk,
                "target_id": target_id,
                "reference": reference,
                "certificate_type": FA_TYPE_CODES[certificate_type],
                "constabulary_id": constabulary_id,
                "date_issued": date_or_none(date_issued),
                "date_issued_str": date_issued,
                "expiry_date": date_or_none(expiry_date),
                "expiry_date_str": expiry_date,
            }
        )


class ImportContact(MigrationBase):
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
    created_datetime = models.DateTimeField(auto_now_add=True)
    updated_datetime = models.DateTimeField(auto_now=True)

    @classmethod
    def parse_xml(cls, batch: list[Tuple[int, str]]) -> list["ImportContact"]:
        """Example XML structure

        <SELLER_HOLDER_LIST>
          <SELLER_HOLDER />
        </SELLER_HOLDER_LIST>
        """

        model_list = []
        for parent_pk, xml_str in batch:
            xml_tree = etree.fromstring(xml_str)
            xml_list = xml_tree.xpath("SELLER_HOLDER")
            for xml in xml_list:
                model_list.append(cls.parse_xml_fields(parent_pk, xml))
        return model_list

    @classmethod
    def parse_xml_fields(cls, parent_pk: int, xml: etree.ElementTree) -> "ImportContact":
        """Example XML structure

        <SELLER_HOLDER>
          <PERSON_DETAILS>
            <PERSON_TYPE />
            <LEGAL_PERSON_NAME />
            <REGISTRATION_NUMBER />
            <FIRST_NAME />
            <SURNAME />
          </PERSON_DETAILS>
          <ADDRESS>
            <STREET_AND_NUMBER />
            <TOWN_CITY />
            <POSTCODE />
            <REGION />
            <COUNTRY />
          </ADDRESS>
          <IS_DEALER_FLAG />
          <SELLER_HOLDER_ID />
          <UPDATE_FLAG />
        </SELLER_HOLDER>
        """

        legacy_id = get_xml_val(xml, "./SELLER_HOLDER_ID/text()")
        entity = get_xml_val(xml, "./PERSON_DETAILS/PERSON_TYPE/text()")
        entity = entity.lower().strip("_person")
        if entity == "legal":
            first_name = get_xml_val(xml, "./PERSON_DETAILS/LEGAL_PERSON_NAME/text()")
        else:
            first_name = get_xml_val(xml, "./PERSON_DETAILS/FIRST_NAME/text()")
        last_name = get_xml_val(xml, "./PERSON_DETAILS/SURNAME/text()")
        registration_number = get_xml_val(xml, "./PERSON_DETAILS/REGISTRATION_NUMBER/text()")
        street = get_xml_val(xml, "./ADDRESS/STREET_AND_NUMBER/text()")
        city = get_xml_val(xml, "./ADDRESS/TOWN_CITY/text()")
        postcode = get_xml_val(xml, "./ADDRESS/POSTCODE/text()")
        region = get_xml_val(xml, "./ADDRESS/REGION/text()")
        dealer = get_xml_val(xml, "./IS_DEALER_FLAG/text()")
        country_id = get_xml_val(xml, "./ADDRESS/COUNTRY/text()")

        return cls(
            **{
                "import_application_id": parent_pk,
                "legacy_id": legacy_id,
                "entity": entity,
                "first_name": first_name,
                "last_name": last_name,
                "registration_number": registration_number,
                "street": street,
                "city": city,
                "postcode": postcode,
                "region": region,
                "dealer": str_to_yes_no(dealer),
                "country_id": country_id,
            }
        )

    @classmethod
    def get_excludes(cls) -> list[str]:
        return super().get_excludes() + ["legacy_id"]


class SupplementaryInfoBase(MigrationBase):
    class Meta:
        abstract = True

    is_complete = models.BooleanField(default=False)
    completed_datetime = models.DateTimeField(null=True)
    completed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="+")
    no_report_reason = models.CharField(
        max_length=1000,
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
            .iterator()
        )

    @classmethod
    def parse_xml(cls, batch: list[Tuple[int, str]]) -> list["SupplementaryReportBase"]:
        """Example XML structure

        <FA_SUPPLEMENTARY_REPORT_LIST>
          <FA_SUPPLEMENTARY_REPORT />
        </FA_SUPPLEMENTARY_REPORT_LIST>
        """
        model_list = []
        for parent_pk, xml in batch:
            xml_tree = etree.fromstring(xml)
            report_xml_list = xml_tree.xpath("FA_SUPPLEMENTARY_REPORT")
            for report_xml in report_xml_list:
                model_list.append(cls.parse_xml_fields(parent_pk, report_xml))
        return model_list

    @classmethod
    def parse_xml_fields(cls, parent_pk: int, xml: etree.ElementTree) -> "SupplementaryReportBase":
        """Example XML structure

        <FA_SUPPLEMENTARY_REPORT>
          <HISTORICAL_REPORT_LIST />
          <FA_SUPPLEMENTARY_REPORT_DETAILS>
            <GOODS_LINE_LIST />
            <MODE_OF_TRANSPORT />
            <RECEIVED_DATE />
            <REPORT_SELLER_HOLDER />
            <REPORT_SUBMITTED_FLAG />
            <SUBMITTED_BY_WUA_ID />
            <SUBMITTED_DATETIME />
            <FA_REPORT_ID />
          </FA_SUPPLEMENTARY_REPORT_DETAILS>
        </FA_SUPPLEMENTARY_REPORT>
        """

        transport = get_xml_val(xml, ".//MODE_OF_TRANSPORT[not(fox-error)]/text()")
        date_received = get_xml_val(xml, ".//RECEIVED_DATE[not(fox-error)]/text()")
        report_firearms_xml = get_xml_val(xml, ".//GOODS_LINE_LIST")
        bought_from_legacy_id = get_xml_val(xml, ".//REPORT_SELLER_HOLDER[not(fox-error)]/text()")

        return cls(
            **{
                "supplementary_info_id": parent_pk,
                "transport": transport,
                "date_received": date_or_none(date_received),
                "bought_from_legacy_id": bought_from_legacy_id,
                "report_firearms_xml": xml_str_or_none(report_firearms_xml),
            }
        )


class SupplementaryReportFirearmBase(MigrationBase):
    class Meta:
        abstract = True

    serial_number = models.CharField(max_length=100, null=True)
    calibre = models.CharField(max_length=400, null=True)
    model = models.CharField(max_length=400, null=True)
    proofing = models.CharField(max_length=3, null=True, default=None)
    is_manual = models.BooleanField(default=False)
    is_upload = models.BooleanField(default=False)
    is_no_firearm = models.BooleanField(default=False)

    @classmethod
    def parse_xml(cls, batch: list[Tuple[int, str]]) -> list["SupplementaryReportFirearmBase"]:
        """Example XML structure

        <GOODS_LINE_LIST>
          <GOODS_LINE>
            <FA_REPORTING_MODE />
            <FIREARMS_DETAILS_LIST>
              <FIREARMS_DETAILS />
            </FIREARMS_DETAILS_LIST>
          </GOODS_LINE>
        </GOODS_LINE_LIST>
        """

        model_list = []
        for parent_pk, xml in batch:
            xml_tree = etree.fromstring(xml)
            goods_xml_list = xml_tree.xpath("GOODS_LINE")
            for goods_xml in goods_xml_list:
                reporting_mode = get_xml_val(goods_xml, "./FA_REPORTING_MODE/text()")
                if reporting_mode == "MANUAL":
                    report_firearm_xml_list = goods_xml.xpath(".//FIREARMS_DETAILS")
                    for report_firearm_xml in report_firearm_xml_list:
                        model_list.append(cls.parse_manual_xml(parent_pk, report_firearm_xml))
                elif reporting_mode == "UPLOAD":
                    model_list.append(cls(report_id=parent_pk, is_upload=True))
                    # TODO ICMSLST-1496: Report firearms need to connect to documents
                    # report_firearm_xml_list = goods_xml.xpath("/FIREARMS_DETAILS_LIST")
                else:
                    # TODO ICMSLST-1496: Check no firearms reported
                    model_list.append(cls(is_no_firearm=True))

        return model_list

    @classmethod
    def parse_manual_xml(
        cls, parent_pk: int, xml: etree.ElementTree
    ) -> "SupplementaryReportFirearmBase":
        """Exmaple XML structure

        <FIREARMS_DETAILS>
          <SERIAL_NUMBER />
          <CALIBRE />
          <MAKE_MODEL />
          <PROOFING />
        </FIREARMS_DETAILS>
        """

        serial_number = get_xml_val(xml, ".//SERIAL_NUMBER/text()")
        calibre = get_xml_val(xml, ".//CALIBRE/text()")
        model = get_xml_val(xml, ".//MAKE_MODEL/text()")
        proofing = get_xml_val(xml, ".//PROOFING/text()")

        return cls(
            **{
                "report_id": parent_pk,
                "serial_number": serial_number,
                "calibre": calibre,
                "model": model,
                "proofing": str_to_yes_no(proofing),
                "is_manual": True,
            }
        )
