import pytest
from django.core import mail
from django.test import TestCase

from web.models import AlternativeEmail, Importer, PersonalEmail, User
from web.notify import constants, email
from web.permissions import organisation_add_contact
from web.tests.domains.exporter.factory import ExporterFactory
from web.tests.domains.importer.factory import ImporterFactory
from web.tests.domains.user.factory import UserFactory

# TODO reimplement mailshot tests with ICMSLST-1968


class TestEmail(TestCase):
    def create_user(self, account_status):
        user = UserFactory(account_status=account_status)
        return user

    def create_importer_org(self, name=None, active=True, members=None):
        if not members:
            members = []

        importer = ImporterFactory(is_active=active, name=name, type=Importer.ORGANISATION)

        for member in members:
            if member["active"]:
                user = self.create_user(account_status=User.ACTIVE)
            else:
                user = self.create_user(account_status=User.CANCELLED)

            for m in member["personal"]:
                PersonalEmail(user=user, email=m["email"], portal_notifications=m["notify"]).save()
            if "alternative" in member:
                for m in member["alternative"]:
                    AlternativeEmail(
                        user=user, email=m["email"], portal_notifications=m["notify"]
                    ).save()

            organisation_add_contact(importer, user)

    def create_individual_importer(self, name=None, active=True, user=None):
        is_active = user["active"]
        if is_active:
            _user = self.create_user(account_status=User.ACTIVE)
        else:
            _user = self.create_user(account_status=User.BLOCKED)

        ImporterFactory(is_active=active, user=_user, name=name, type=Importer.INDIVIDUAL)
        for m in user["personal"]:
            PersonalEmail(user=_user, email=m["email"], portal_notifications=m["notify"]).save()

    def create_exporter(self, name=None, active=True, members=None):
        if not members:
            members = []

        exporter = ExporterFactory(is_active=active, name=name)

        for member in members:
            if member["active"]:
                user = self.create_user(account_status=User.ACTIVE)
            else:
                user = self.create_user(account_status=User.CANCELLED)

            for m in member["personal"]:
                PersonalEmail(user=user, email=m["email"], portal_notifications=m["notify"]).save()
            if "alternative" in member:
                for m in member["alternative"]:
                    AlternativeEmail(
                        user=user, email=m["email"], portal_notifications=m["notify"]
                    ).save()

            organisation_add_contact(exporter, user)

    def setup_importers(self):
        # An active import organisation
        self.create_importer_org(
            name="An import organisation",
            members=[
                {
                    "active": True,
                    "personal": [
                        {"email": "active_org_user@example.com", "notify": True},  # /PS-IGNORE
                        {
                            "email": "active_org_user_second_email@example.com",  # /PS-IGNORE
                            "notify": True,
                        },
                        {
                            "email": "active_org_user_no_notify@example.com",  # /PS-IGNORE
                            "notify": False,
                        },
                    ],
                    "alternative": [
                        {"email": "active_org_user_alt@example.com", "notify": True},  # /PS-IGNORE
                        {
                            "email": "active_org_user_alt_no_notify@example.com",  # /PS-IGNORE
                            "notify": False,
                        },
                    ],
                },
                {
                    "active": True,
                    "personal": [
                        {
                            "email": "second_active_org_user@example.com",  # /PS-IGNORE
                            "notify": True,
                        }
                    ],
                    "alternative": [
                        {
                            "email": "second_active_org_user_alt@example.com",  # /PS-IGNORE
                            "notify": True,
                        }
                    ],
                },
                {
                    "active": False,
                    "personal": [
                        {"email": "deactive_org_user@example.com", "notify": True}  # /PS-IGNORE
                    ],
                },
            ],
        )

        # An archived import organisation
        self.create_importer_org(
            name="Another import organisation",
            active=False,
            members=[
                {
                    "active": True,
                    "personal": [
                        {"email": "archived_org_user@example.com", "notify": True}  # /PS-IGNORE
                    ],
                    "alternative": [
                        {"email": "archived_org_user_alt@example.com", "notify": True}  # /PS-IGNORE
                    ],
                },
            ],
        )

        # An active individual importer
        self.create_individual_importer(
            active=True,
            name="An individual importer",
            user={
                "active": True,
                "personal": [
                    {"email": "ind_importer_user@example.com", "notify": True},  # /PS-IGNORE
                    {"email": "ind_importer_no_notify@example.com", "notify": False},  # /PS-IGNORE
                ],
            },
        )

        # An archived individual importer
        self.create_individual_importer(
            active=False,
            name="Another individual importer",
            user={
                "active": True,
                "personal": [
                    {
                        "email": "deactive_ind_importer_user@example.com",  # /PS-IGNORE
                        "notify": True,
                    },
                    {
                        "email": "deactive_ind_importer_no_notify@example.com",  # /PS-IGNORE
                        "notify": False,
                    },
                ],
            },
        )

    def setup_exporters(self):
        # An active exporter
        self.create_exporter(
            name="An exporter",
            members=[
                {
                    "active": True,
                    "personal": [
                        {"email": "active_export_user@example.com", "notify": True},  # /PS-IGNORE
                        {
                            "email": "active_export_user_no_notify@example.com",  # /PS-IGNORE
                            "notify": False,
                        },
                    ],
                    "alternative": [
                        {
                            "email": "active_export_user_alt@example.com",  # /PS-IGNORE
                            "notify": True,
                        },
                        {
                            "email": "active_export_user_alt_no_notify@example.com",  # /PS-IGNORE
                            "notify": False,
                        },
                    ],
                },
                {
                    "active": True,
                    "personal": [
                        {
                            "email": "second_active_export_user@example.com",  # /PS-IGNORE
                            "notify": True,
                        }
                    ],
                },
                {
                    "active": False,
                    "personal": [
                        {"email": "deactive_export_user@example.com", "notify": True}  # /PS-IGNORE
                    ],
                },
            ],
        )

        # An archived import organisation
        self.create_exporter(
            name="Another exporter",
            active=False,
            members=[
                {
                    "active": True,
                    "personal": [
                        {"email": "archived_export_user@example.com", "notify": True}  # /PS-IGNORE
                    ],
                    "alternative": [
                        {
                            "email": "archived_export_user_alt@example.com",  # /PS-IGNORE
                            "notify": True,
                        }
                    ],
                },
            ],
        )

    def setUp(self):
        self.setup_importers()
        self.setup_exporters()

    def test_send_email(self):
        email.send_email.delay(
            "Test subject",
            "Test message",
            ["test@example.com", "test2@example.com"],  # /PS-IGNORE
            html_message="<p>Test message</p>",
        )
        outbox = mail.outbox
        assert len(outbox) == 1
        assert "test@example.com" in outbox[0].to  # /PS-IGNORE
        assert "test2@example.com" in outbox[0].to  # /PS-IGNORE

    def test_multipart_email(self):
        email.send_email("Subject", "Message", ["test@example.com", "<p>Message</p>"])  # /PS-IGNORE
        m = mail.outbox[0]
        assert isinstance(m, mail.EmailMultiAlternatives)

    def test_mail_subject(self):
        email.send_email("Subject", "Message", ["test@example.com", "<p>Message</p>"])  # /PS-IGNORE
        m = mail.outbox[0]
        assert m.subject == "Subject"

    def test_mail_body(self):
        email.send_email("Subject", "Message", ["test@example.com", "<p>Message</p>"])  # /PS-IGNORE
        m = mail.outbox[0]
        assert m.body == "Message"

    def test_mail_from(self):
        email.send_email("Subject", "Message", ["test@example.com", "<p>Message</p>"])  # /PS-IGNORE
        m = mail.outbox[0]

        # Set in config/settings/non_prod_base.py
        assert m.from_email == "enquiries.ilb@icms.trade.dev.uktrade.io"  # /PS-IGNORE

    def test_mail_to(self):
        email.send_email(
            "Subject",
            "Message",
            ["test@example.com", "test2@example.com", "<p>Message</p>"],  # /PS-IGNORE
        )
        m = mail.outbox[0]
        assert m.to[0] == "test@example.com"  # /PS-IGNORE
        assert m.to[1] == "test2@example.com"  # /PS-IGNORE

    def test_send_mailshot_to_importers(self):
        email.send_mailshot.delay(
            "Test subject", "Test message", html_message="<p>Test message</p>", to_importers=True
        )
        outbox = mail.outbox
        assert len(outbox) == 7
        # Many-to-many relations order is not guaranteed
        # Members of exporter team might have different order
        # Testing by length
        for o in outbox:
            if len(o.to) == 3:
                assert "active_org_user@example.com" in o.to  # /PS-IGNORE
                assert "active_org_user_second_email@example.com" in o.to  # /PS-IGNORE
                assert "active_org_user_alt@example.com" in o.to  # /PS-IGNORE
            elif len(o.to) == 2:
                assert "second_active_org_user@example.com" in o.to  # /PS-IGNORE
                assert "second_active_org_user_alt@example.com" in o.to  # /PS-IGNORE
            elif len(o.to) == 1:
                pass
            else:
                raise AssertionError(o.to)

    def test_send_mailshot_to_exporters(self):
        email.send_mailshot.delay(
            "Test subject", "Test message", html_message="<p>Test message</p>", to_exporters=True
        )
        outbox = mail.outbox
        assert len(outbox) == 6
        # Many-to-many relations order is not guaranteed
        # Members of exporter team might have different order
        # Testing by length
        for o in outbox:
            if len(o.to) == 2:
                assert "active_export_user@example.com" in o.to  # /PS-IGNORE
                assert "active_export_user_alt@example.com" in o.to  # /PS-IGNORE
            elif len(o.to) == 1:
                pass
            else:
                raise AssertionError(o.to)


@pytest.mark.django_db
def test_send_to_application_contacts_import(fa_sil_app_submitted):
    email.send_to_application_contacts(fa_sil_app_submitted, "Test", "Test Body")
    outbox = mail.outbox
    assert len(outbox) == 1

    o = outbox[0]
    assert o.to == ["I1_main_contact@example.com"]  # /PS-IGNORE
    assert o.subject == "Test"
    assert o.body == "Test Body"


@pytest.mark.django_db
def test_send_to_application_agent_import(fa_sil_app_submitted, agent_importer):
    fa_sil_app_submitted.agent = agent_importer
    email.send_to_application_contacts(fa_sil_app_submitted, "Test", "Test Body")
    outbox = mail.outbox

    assert len(outbox) == 1
    o = outbox[0]
    assert o.to == ["I1_A1_main_contact@example.com"]  # /PS-IGNORE
    assert o.subject == "Test"
    assert o.body == "Test Body"


@pytest.mark.django_db
def test_send_to_application_contacts_export(com_app_submitted):
    email.send_to_application_contacts(com_app_submitted, "Test", "Test Body")
    outbox = mail.outbox
    assert len(outbox) == 1

    o = outbox[0]
    assert o.to == ["E1_main_contact@example.com"]  # /PS-IGNORE
    assert o.subject == "Test"
    assert o.body == "Test Body"


@pytest.mark.django_db
def test_send_to_application_agent_export(com_app_submitted, agent_exporter):
    com_app_submitted.agent = agent_exporter
    com_app_submitted.save()
    email.send_to_application_contacts(com_app_submitted, "Test", "Test Body")
    outbox = mail.outbox

    assert len(outbox) == 1
    o = outbox[0]
    assert o.to == ["E1_A1_main_contact@example.com"]  # /PS-IGNORE
    assert o.subject == "Test"
    assert o.body == "Test Body"


def test_send_refused_email_import(complete_rejected_app):
    _check_send_refused_email(complete_rejected_app, "I1_main_contact@example.com")  # /PS-IGNORE


def test_send_refused_email_export(complete_rejected_export_app):
    _check_send_refused_email(
        complete_rejected_export_app, "E1_main_contact@example.com"  # /PS-IGNORE
    )


def _check_send_refused_email(app, expected_to_email):
    outbox = mail.outbox

    assert len(outbox) == 1
    first_email = outbox[0]
    assert first_email.to == [expected_to_email]
    assert first_email.subject == f"Application reference {app.reference} has been refused by ILB."
    assert "has been refused by ILB" in first_email.body
    assert app.refuse_reason in first_email.body


def test_send_database_email(com_app_submitted):
    email.send_database_email(com_app_submitted, constants.DatabaseEmailTemplate.STOP_CASE)
    outbox = mail.outbox
    assert len(outbox) == 1

    sent_email = outbox[0]
    assert sent_email.to == ["E1_main_contact@example.com"]  # /PS-IGNORE
    assert sent_email.subject == f"ICMS Case Reference {com_app_submitted.reference} Stopped"
    assert (
        f"Processing on ICMS Case Reference {com_app_submitted.reference} has been stopped"
    ) in sent_email.body
