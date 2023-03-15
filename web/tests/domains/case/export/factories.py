import factory

from web.models import (
    CertificateOfFreeSaleApplication,
    CertificateOfGoodManufacturingPracticeApplication,
    CertificateOfManufactureApplication,
    CFSSchedule,
    ExportApplicationType,
)
from web.tests.domains.exporter.factory import ExporterFactory
from web.tests.domains.user.factory import UserFactory


class CertificateOfManufactureApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CertificateOfManufactureApplication

    process_type = CertificateOfManufactureApplication.PROCESS_TYPE

    application_type = factory.Iterator(ExportApplicationType.objects.filter(type_code="COM"))
    created_by = factory.SubFactory(UserFactory)
    exporter = factory.SubFactory(ExporterFactory)
    last_updated_by = factory.SubFactory(UserFactory)


class CertificateOfGMPApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CertificateOfGoodManufacturingPracticeApplication

    process_type = CertificateOfGoodManufacturingPracticeApplication.PROCESS_TYPE
    application_type = factory.Iterator(ExportApplicationType.objects.filter(type_code="GMP"))
    created_by = factory.SubFactory(UserFactory)
    exporter = factory.SubFactory(ExporterFactory)
    last_updated_by = factory.SubFactory(UserFactory)


class CertificateOfFreeSaleApplicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CertificateOfFreeSaleApplication

    process_type = CertificateOfFreeSaleApplication.PROCESS_TYPE

    application_type = factory.Iterator(ExportApplicationType.objects.filter(type_code="CFS"))
    created_by = factory.SubFactory(UserFactory)
    exporter = factory.SubFactory(ExporterFactory)
    last_updated_by = factory.SubFactory(UserFactory)


class CFSScheduleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CFSSchedule

    created_by = factory.SubFactory(UserFactory)
