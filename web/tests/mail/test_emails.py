import pytest
from django.conf import settings

from web.mail import emails
from web.mail.constants import EmailTypes
from web.models import EmailTemplate, ImporterAccessRequest
from web.tests.auth.auth import AuthTestCase


def default_personalisation() -> dict:
    return {
        "icms_url": settings.DEFAULT_DOMAIN,
        "icms_contact_email": settings.ILB_CONTACT_EMAIL,
        "icms_contact_phone": settings.ILB_CONTACT_PHONE,
        "subject": "",
        "body": "",
    }


class TestEmails(AuthTestCase):
    @pytest.fixture(autouse=True)
    def setup(self, _setup, mock_gov_notify_client):
        self.mock_gov_notify_client = mock_gov_notify_client

    def test_access_request_email(self, importer_access_request):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.ACCESS_REQUEST).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": importer_access_request.reference
        }
        emails.send_access_requested_email(importer_access_request)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 2
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_two_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_access_request_closed_email(self, importer_access_request):
        importer_access_request.response = ImporterAccessRequest.APPROVED
        importer_access_request.request_type = ImporterAccessRequest.AGENT_ACCESS

        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.ACCESS_REQUEST_CLOSED).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "agent": "Agent ",
            "organisation": "Import Ltd",
            "outcome": "Approved",
            "reason": "",
            "request_type": "Importer",
        }
        emails.send_access_request_closed_email(importer_access_request)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            importer_access_request.submitted_by.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )
