import pytest

from web.domains.case._import.fa_dfl.models import DFLApplication
from web.domains.case._import.fa_oil.models import OpenIndividualLicenceApplication
from web.domains.country.models import Country
from web.domains.importer.models import Importer
from web.domains.office.models import Office


@pytest.fixture()
def importer():
    return Importer(eori_number="GB123456789", type=Importer.ORGANISATION, name="Importer Name")


@pytest.fixture()
def importer_office():
    return Office(postcode="S93bl", address="""22 Some Avenue\nSome Way\nSome Town""")  # /PS-IGNORE


@pytest.fixture()
def oil_app(importer, importer_office):
    oil_app = OpenIndividualLicenceApplication(
        applicant_reference="Applicant Reference",
        process_type=OpenIndividualLicenceApplication.PROCESS_TYPE,
        importer=importer,
        importer_office=importer_office,
    )

    return oil_app


@pytest.fixture()
def dfl_app(importer, importer_office):
    dfl_app = DFLApplication(
        applicant_reference="Applicant Reference",
        process_type=DFLApplication.PROCESS_TYPE,
        importer=importer,
        importer_office=importer_office,
        consignment_country=Country(name="Spain"),
        origin_country=Country(name="Italy"),
    )

    return dfl_app


@pytest.fixture()
def oil_expected_preview_context():
    """Returns the minimum expected context values - tests then override the different keys in the tests."""

    return {
        "applicant_reference": "Applicant Reference",
        "importer_name": "Importer Name",
        "consignment_country": "Any Country",
        "origin_country": "Any Country",
        "goods_description": (
            "Firearms, component parts thereof, or ammunition of any applicable "
            "commodity code, other than those falling under Section 5 of the "
            "Firearms Act 1968 as amended."
        ),
        "licence_start_date": "Licence Start Date not set",
        "licence_end_date": "Licence End Date not set",
        "licence_number": "[[Licence Number]]",
        "eori_numbers": ["GB123456789"],
        "importer_address": ["22 Some Avenue", "Some Way", "Some Town"],
        "importer_postcode": "S93bl",  # /PS-IGNORE
        "endorsements": [],
    }


@pytest.fixture()
def dfl_expected_preview_context():
    """Returns the minimum expected context values - tests then override the different keys in the tests."""

    return {
        "applicant_reference": "Applicant Reference",
        "importer_name": "Importer Name",
        "consignment_country": "Spain",
        "origin_country": "Italy",
        "goods": [],
        "licence_start_date": "Licence Start Date not set",
        "licence_end_date": "Licence End Date not set",
        "licence_number": "[[Licence Number]]",
        "eori_numbers": ["GB123456789"],
        "importer_address": ["22 Some Avenue", "Some Way", "Some Town"],
        "importer_postcode": "S93bl",  # /PS-IGNORE
        "endorsements": [],
    }
