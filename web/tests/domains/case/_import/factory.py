import factory.fuzzy

from web.domains.case._import.derogations.models import DerogationsApplication
from web.domains.case._import.firearms.models import OpenIndividualLicenceApplication
from web.domains.case._import.models import ImportApplicationType
from web.domains.case._import.sanctions.models import (
    SanctionsAndAdhocApplication,
    SanctionsAndAdhocApplicationGoods,
)


class OILApplicationFactory(factory.django.DjangoModelFactory):
    process_type = OpenIndividualLicenceApplication.PROCESS_TYPE
    application_type = factory.Iterator(
        ImportApplicationType.objects.filter(
            type=ImportApplicationType.TYPE_FIREARMS_AMMUNITION_CODE,
            sub_type=ImportApplicationType.SUBTYPE_OPEN_INDIVIDUAL_LICENCE,
        )
    )

    class Meta:
        model = OpenIndividualLicenceApplication


class SanctionsAndAdhocLicenseApplicationFactory(factory.django.DjangoModelFactory):
    process_type = SanctionsAndAdhocApplication.PROCESS_TYPE
    application_type = factory.Iterator(
        ImportApplicationType.objects.filter(type=ImportApplicationType.TYPE_SANCTION_ADHOC)
    )

    class Meta:
        model = SanctionsAndAdhocApplication


class SanctionsAndAdhocApplicationGoodsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SanctionsAndAdhocApplicationGoods


class DerogationsApplicationFactory(factory.django.DjangoModelFactory):
    process_type = DerogationsApplication.PROCESS_TYPE
    application_type = factory.Iterator(
        ImportApplicationType.objects.filter(
            type=ImportApplicationType.TYPE_DEGROGATION_FROM_SANCTIONS_BAN
        )
    )

    class Meta:
        model = DerogationsApplication
