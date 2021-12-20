import logging

from django.test import TestCase
from guardian.shortcuts import assign_perm

from web.domains.case._import.forms import (
    CreateImportApplicationForm,
    CreateWoodQuotaApplicationForm,
)
from web.tests.domains.importer.factory import AgentImporterFactory, ImporterFactory
from web.tests.domains.office.factory import OfficeFactory
from web.tests.domains.user.factory import ActiveUserFactory

logger = logging.getLogger(__name__)


class TestCreateOpenIndividualImportLicenceForm(TestCase):
    def test_form_valid(self):
        office = OfficeFactory.create(is_active=True)
        importer = ImporterFactory.create(is_active=True, offices=[office])
        contact = ActiveUserFactory.create()
        assign_perm("web.is_contact_of_importer", contact, importer)

        form = CreateImportApplicationForm(
            data={
                "importer": importer.pk,
                "importer_office": office.pk,
            },
            user=contact,
        )
        self.assertTrue(form.is_valid())

    def test_agent_form_valid(self):
        office_importer, office_agent = OfficeFactory.create_batch(2, is_active=True)

        agent = AgentImporterFactory(main_importer_offices=[office_importer])
        agent.offices.add(office_agent)

        contact = ActiveUserFactory.create()
        assign_perm("web.is_agent_of_importer", contact, agent.main_importer)
        assign_perm("web.is_contact_of_importer", contact, agent)

        form = CreateImportApplicationForm(
            data={
                "importer": agent.main_importer.pk,
                "importer_office": office_importer.pk,
                "agent": agent.pk,
                "agent_office": office_agent.pk,
            },
            user=contact,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_form_message(self):
        office = OfficeFactory.create(is_active=True)
        importer = ImporterFactory.create(is_active=True, offices=[office])
        contact = ActiveUserFactory.create()
        assign_perm("web.is_contact_of_importer", contact, importer)

        form = CreateImportApplicationForm(data={}, user=contact)
        logger.debug(form.errors)
        self.assertEqual(len(form.errors), 2)
        message = form.errors["importer"][0]
        self.assertEqual(message, "You must enter this item")

    def test_wood_application_valid_for_ni_importer(self):
        office = OfficeFactory.create(is_active=True, postcode="BT328bz")  # /PS-IGNORE
        importer = ImporterFactory.create(is_active=True, offices=[office])
        user = ActiveUserFactory.create()
        assign_perm("web.is_contact_of_importer", user, importer)

        form = CreateWoodQuotaApplicationForm(
            data={
                "importer": importer.pk,
                "importer_office": office.pk,
            },
            user=user,
        )

        self.assertTrue(form.is_valid(), "Form has errors")

    def test_wood_application_invalid_for_english_importer(self):
        office = OfficeFactory.create(is_active=True, postcode="S410SG")  # /PS-IGNORE
        importer = ImporterFactory.create(is_active=True, offices=[office])
        user = ActiveUserFactory.create()
        assign_perm("web.is_contact_of_importer", user, importer)

        form = CreateWoodQuotaApplicationForm(
            data={
                "importer": importer.pk,
                "importer_office": office.pk,
            },
            user=user,
        )

        self.assertTrue(form.has_error("importer_office"))
        self.assertEqual(len(form.errors), 1)

        error_message = form.errors["importer_office"][0]
        self.assertEqual(
            error_message, "Wood applications can only be made for Northern Ireland traders."
        )
