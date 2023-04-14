from django.test import TestCase

from web.models import Constabulary


class TestConstabulary(TestCase):
    def create_constabulary(
        self,
        name="Test Constabulary",
        region=Constabulary.EAST_MIDLANDS,
        email="test_constabulary@test.com",  # /PS-IGNORE
        is_active=True,
    ):
        return Constabulary.objects.create(
            name=name, region=region, email=email, is_active=is_active
        )

    def test_create_constabulary(self):
        constabulary = self.create_constabulary()
        assert isinstance(constabulary, Constabulary)
        assert constabulary.name == "Test Constabulary"
        assert constabulary.email == "test_constabulary@test.com"  # /PS-IGNORE
        assert constabulary.region == Constabulary.EAST_MIDLANDS
        assert constabulary.is_active is True

    def test_archive_constabulary(self):
        constabulary = self.create_constabulary()
        constabulary.archive()
        assert constabulary.is_active is False

    def test_unarchive_constabulary(self):
        constabulary = self.create_constabulary()
        constabulary.unarchive()
        assert constabulary.is_active is True

    def test_region_verbose(self):
        constabulary = self.create_constabulary()
        assert constabulary.region_verbose == "East Midlands"

    def test_string_representation(self):
        constabulary = self.create_constabulary()
        assert constabulary.__str__() == f"Constabulary ({constabulary.name})"
