from django.contrib.auth.models import Permission
from django.test import TestCase

from web.domains.constabulary.models import Constabulary
from web.domains.team.models import Role


class ConstabularyTest(TestCase):
    def create_constabulary(
        self,
        name='Test Constabulary',
        region=Constabulary.EAST_MIDLANDS,
        email='test_constabulary@test.com',
        is_active=True,
    ):
        return Constabulary.objects.create(name=name,
                                           region=region,
                                           email=email,
                                           is_active=is_active)

    def test_create_constabulary(self):
        constabulary = self.create_constabulary()
        self.assertTrue(isinstance(constabulary, Constabulary))
        self.assertEqual(constabulary.name, 'Test Constabulary')
        self.assertEqual(constabulary.email, 'test_constabulary@test.com')
        self.assertEqual(constabulary.region, Constabulary.EAST_MIDLANDS)
        self.assertTrue(constabulary.is_active)

    def test_archive_constabulary(self):
        constabulary = self.create_constabulary()
        constabulary.archive()
        self.assertFalse(constabulary.is_active)

    def test_unarchive_constabulary(self):
        constabulary = self.create_constabulary()
        constabulary.unarchive()
        self.assertTrue(constabulary.is_active)

    def test_firearms_authority_role_created(self):
        constabulary = self.create_constabulary()
        role_name = f'Constabulary Contacts:Verified Firearms Authority Editor:{constabulary.id}'
        self.assertTrue(Role.objects.filter(name=role_name).exists())

    def test_firearms_authority_permission_created(self):
        constabulary = self.create_constabulary()
        codename = f'IMP_CONSTABULARY_CONTACTS:FIREARMS_AUTHORITY_EDITOR:{constabulary.id}:IMP_EDIT_FIREARMS_AUTHORITY'  # noqa: C0301
        self.assertTrue(Permission.objects.filter(codename=codename).exists())

    def test_region_verbose(self):
        constabulary = self.create_constabulary()
        self.assertEqual(constabulary.region_verbose, 'East Midlands')

    def test_string_representation(self):
        constabulary = self.create_constabulary()
        self.assertEqual(constabulary.__str__(),
                         f'Constabulary ({constabulary.name})')
