import pytest

from web.domains.case.export.forms import EditGMPForm

from .factories import CertificateOfGMPApplicationFactory


@pytest.mark.django_db
def test_gmp_form_clean_ni_postcode_gb_country(mocker):
    form_mock = mocker.patch("web.domains.case.export.forms.EditGMPForm.is_valid")
    form_mock.return_value = True
    instance = CertificateOfGMPApplicationFactory()

    form = EditGMPForm(
        instance=instance,
        data={
            "manufacturer_postcode": "BT43XX",
            "manufacturer_country": "GB",
            "responsible_person_postcode": "BT43XX",
            "responsible_person_country": "GB",
            "is_responsible_person": "yes",
            "gmp_certificate_issued": "BRC_GSOCP",
        },
    )
    form.cleaned_data = form.data
    form.clean()
    assert form.errors["responsible_person_postcode"][0] == "Postcode should not start with BT"
    assert form.errors["manufacturer_postcode"][0] == "Postcode should not start with BT"


@pytest.mark.django_db
def test_gmp_form_clean_gb_postcode_ni_country(mocker):
    form_mock = mocker.patch("web.domains.case.export.forms.EditGMPForm.is_valid")
    form_mock.return_value = True
    instance = CertificateOfGMPApplicationFactory()

    form = EditGMPForm(
        instance=instance,
        data={
            "manufacturer_postcode": "SW1A1AA",
            "manufacturer_country": "NIR",
            "responsible_person_postcode": "SW1A1AA",
            "responsible_person_country": "NIR",
            "is_responsible_person": "yes",
            "gmp_certificate_issued": "BRC_GSOCP",
        },
    )
    form.cleaned_data = form.data
    form.clean()
    assert form.errors["responsible_person_postcode"][0] == "Postcode must start with BT"
    assert form.errors["manufacturer_postcode"][0] == "Postcode must start with BT"