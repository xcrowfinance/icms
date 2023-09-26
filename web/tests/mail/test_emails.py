from unittest import mock

import pytest
from django.conf import settings

from web.mail import emails
from web.mail.constants import EmailTypes, VariationRequestDescription
from web.mail.url_helpers import get_case_view_url, get_validate_digital_signatures_url
from web.models import (
    EmailTemplate,
    ExporterAccessRequest,
    ImporterAccessRequest,
    VariationRequest,
    WithdrawApplication,
)
from web.sites import (
    get_caseworker_site_domain,
    get_exporter_site_domain,
    get_importer_site_domain,
)
from web.tests.auth.auth import AuthTestCase
from web.tests.helpers import (
    add_approval_request,
    add_variation_request_to_app,
    get_linked_access_request,
)


def default_personalisation() -> dict:
    return {
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
            "reference": importer_access_request.reference,
            "icms_url": get_caseworker_site_domain(),
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

    def test_importer_access_request_closed_email(self, importer_access_request):
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
            "icms_url": get_importer_site_domain(),
        }
        emails.send_access_request_closed_email(importer_access_request)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            importer_access_request.submitted_by.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_exporter_access_request_closed_email(self, exporter_access_request):
        exporter_access_request.response = ExporterAccessRequest.REFUSED
        exporter_access_request.request_type = ExporterAccessRequest.MAIN_EXPORTER_ACCESS

        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.ACCESS_REQUEST_CLOSED).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "agent": "",
            "organisation": "Export Ltd",
            "outcome": "Refused",
            "reason": "",
            "request_type": "Exporter",
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_access_request_closed_email(exporter_access_request)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            exporter_access_request.submitted_by.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_access_request_closed_request_type_email(self, exporter_access_request):
        exporter_access_request.REQUEST_TYPE = "UNKNOWN"
        with pytest.raises(ValueError, match="Unknown access request type: UNKNOWN"):
            emails.send_access_request_closed_email(exporter_access_request)

    def test_exporter_send_approval_request_opened_email(self, exporter_access_request):
        ear = get_linked_access_request(exporter_access_request, self.exporter)
        ear_approval = add_approval_request(ear, self.ilb_admin_user, self.exporter_user)

        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.EXPORTER_ACCESS_REQUEST_APPROVAL_OPENED
            ).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "user_type": "user",
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_approval_request_opened_email(ear_approval)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.exporter_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_importer_send_approval_request_opened_email(self, importer_access_request):
        iar = get_linked_access_request(importer_access_request, self.importer)
        iar.agent_link = self.importer_agent
        iar.request_type = ImporterAccessRequest.AGENT_ACCESS
        iar.save()

        iar_approval = add_approval_request(iar, self.ilb_admin_user, self.importer_user)

        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.IMPORTER_ACCESS_REQUEST_APPROVAL_OPENED
            ).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "user_type": "agent",
            "icms_url": get_importer_site_domain(),
        }
        emails.send_approval_request_opened_email(iar_approval)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.importer_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_approval_request_completed_email(self, exporter_access_request):
        ear = get_linked_access_request(exporter_access_request, self.exporter)
        ear_approval = add_approval_request(ear, self.ilb_admin_user, self.exporter_user)

        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.ACCESS_REQUEST_APPROVAL_COMPLETE
            ).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "user_type": "user",
            "icms_url": get_caseworker_site_domain(),
        }
        emails.send_approval_request_completed_email(ear_approval)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 2
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_two_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_application_stopped_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.APPLICATION_STOPPED).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_application_stopped_email(completed_cfs_app)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "E1_main_contact@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_application_reopened_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.APPLICATION_REOPENED).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_application_reopened_email(completed_cfs_app)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "E1_main_contact@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    @pytest.mark.parametrize(
        "comment,expected_comment",
        [
            ("Reassigned this case to you.", "Reassigned this case to you."),
            ("", "None provided."),
        ],
    )
    def test_send_application_reassigned_email(
        self, com_app_submitted, ilb_admin_two, comment, expected_comment
    ):
        com_app_submitted.case_owner = ilb_admin_two
        com_app_submitted.save()

        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.APPLICATION_REASSIGNED).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": com_app_submitted.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(com_app_submitted, get_caseworker_site_domain()),
            "comment": expected_comment,
            "icms_url": get_caseworker_site_domain(),
        }

        emails.send_application_reassigned_email(com_app_submitted, comment)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "ilb_admin_two@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_application_refused_email(self, fa_sil_app_submitted):
        fa_sil_app_submitted.decision = fa_sil_app_submitted.REFUSE
        fa_sil_app_submitted.refuse_reason = "Application Incomplete"
        fa_sil_app_submitted.save()
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.APPLICATION_REFUSED).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": fa_sil_app_submitted.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(fa_sil_app_submitted, get_importer_site_domain()),
            "reason": fa_sil_app_submitted.refuse_reason,
            "icms_url": get_importer_site_domain(),
        }
        emails.send_application_refused_email(fa_sil_app_submitted)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "I1_main_contact@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_application_complete_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.APPLICATION_COMPLETE).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_application_complete_email(completed_cfs_app)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "E1_main_contact@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_application_variation_complete_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_VARIATION_REQUEST_COMPLETE
            ).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_application_variation_complete_email(completed_cfs_app)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "E1_main_contact@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_application_extension_complete_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_EXTENSION_COMPLETE
            ).gov_notify_template_id
        )
        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_application_extension_complete_email(completed_cfs_app)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "E1_main_contact@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_withdrawal_opened_email(self, com_app_submitted):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.WITHDRAWAL_OPENED).gov_notify_template_id
        )
        withdrawal = com_app_submitted.withdrawals.create(
            status=WithdrawApplication.Statuses.OPEN,
            request_by=self.importer_user,
            reason="Raised in error",
        )

        expected_personalisation = default_personalisation() | {
            "reference": com_app_submitted.reference,
            "reason": "Raised in error",
            "icms_url": get_caseworker_site_domain(),
        }
        emails.send_withdrawal_email(withdrawal)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 2
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "ilb_admin_user@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            "ilb_admin_two@example.com",  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_withdrawal_accepted_email(self, com_app_submitted):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.WITHDRAWAL_ACCEPTED).gov_notify_template_id
        )
        withdrawal = com_app_submitted.withdrawals.create(
            status=WithdrawApplication.Statuses.ACCEPTED, request_by=self.exporter_user
        )

        expected_personalisation = default_personalisation() | {
            "reference": com_app_submitted.reference,
            "reason": "",
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_withdrawal_email(withdrawal)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.exporter_user.email,  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_withdrawal_cancelled_email(self, com_app_submitted):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.WITHDRAWAL_CANCELLED).gov_notify_template_id
        )
        withdrawal = com_app_submitted.withdrawals.create(
            status=WithdrawApplication.Statuses.DELETED, request_by=self.exporter_user
        )

        expected_personalisation = default_personalisation() | {
            "reference": com_app_submitted.reference,
            "reason": "",
            "icms_url": get_caseworker_site_domain(),
        }
        emails.send_withdrawal_email(withdrawal)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 2
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_user.email,  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_two_user.email,  # /PS-IGNORE
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_withdrawal_rejected_email(self, com_app_submitted):
        exp_template_id = str(
            EmailTemplate.objects.get(name=EmailTypes.WITHDRAWAL_REJECTED).gov_notify_template_id
        )
        withdrawal = com_app_submitted.withdrawals.create(
            status=WithdrawApplication.Statuses.REJECTED,
            request_by=self.exporter_user,
            response="Invalid",
        )
        expected_personalisation = default_personalisation() | {
            "reference": com_app_submitted.reference,
            "reason": "",
            "reason_rejected": "Invalid",
            "icms_url": get_exporter_site_domain(),
        }
        emails.send_withdrawal_email(withdrawal)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.exporter_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_withdrawal_unsupported_status_error(self, com_app_submitted):
        withdrawal = com_app_submitted.withdrawals.create(
            status="",
            request_by=self.importer_user,
        )
        with pytest.raises(ValueError, match="Unsupported Withdrawal Status"):
            emails.send_withdrawal_email(withdrawal)
            assert self.mock_gov_notify_client.send_email_notification.call_count == 0

    def test_send_variation_request_unsupported_status_error(self, completed_cfs_app):
        vr = add_variation_request_to_app(
            completed_cfs_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.OPEN,
        )
        with pytest.raises(ValueError, match="Unsupported Variation Request Description"):
            emails.send_variation_request_email(vr, None, completed_cfs_app)
            assert self.mock_gov_notify_client.send_email_notification.call_count == 0

    def test_send_variation_request_cancelled_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_VARIATION_REQUEST_CANCELLED
            ).gov_notify_template_id
        )
        vr = add_variation_request_to_app(
            completed_cfs_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.CANCELLED,
        )
        vr.reject_cancellation_reason = "Cancel reason"
        vr.save()

        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "reason": "Cancel reason",
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "icms_url": get_caseworker_site_domain(),
            "application_url": get_case_view_url(completed_cfs_app, get_caseworker_site_domain()),
        }
        emails.send_variation_request_email(
            vr, VariationRequestDescription.CANCELLED, completed_cfs_app
        )
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_variation_request_update_required_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_VARIATION_REQUEST_UPDATE_REQUIRED
            ).gov_notify_template_id
        )
        vr = add_variation_request_to_app(
            completed_cfs_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.OPEN,
        )
        vr.update_request_reason = "Please update"
        vr.save()

        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "reason": "Please update",
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "icms_url": get_exporter_site_domain(),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
        }
        emails.send_variation_request_email(
            vr, VariationRequestDescription.UPDATE_REQUIRED, completed_cfs_app
        )
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.exporter_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_variation_request_update_cancelled_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_VARIATION_REQUEST_UPDATE_CANCELLED
            ).gov_notify_template_id
        )
        vr = add_variation_request_to_app(
            completed_cfs_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.OPEN,
        )

        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "icms_url": get_exporter_site_domain(),
            "application_url": get_case_view_url(completed_cfs_app, get_exporter_site_domain()),
        }
        emails.send_variation_request_email(
            vr, VariationRequestDescription.UPDATE_CANCELLED, completed_cfs_app
        )
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.exporter_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_variation_request_update_received_email(self, completed_cfs_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_VARIATION_REQUEST_UPDATE_RECEIVED
            ).gov_notify_template_id
        )
        vr = add_variation_request_to_app(
            completed_cfs_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.OPEN,
        )

        expected_personalisation = default_personalisation() | {
            "reference": completed_cfs_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "icms_url": get_caseworker_site_domain(),
            "application_url": get_case_view_url(completed_cfs_app, get_caseworker_site_domain()),
        }
        emails.send_variation_request_email(
            vr, VariationRequestDescription.UPDATE_RECEIVED, completed_cfs_app
        )
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.ilb_admin_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_variation_request_refused_email(self, completed_dfl_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.APPLICATION_VARIATION_REQUEST_REFUSED
            ).gov_notify_template_id
        )
        vr = add_variation_request_to_app(
            completed_dfl_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.OPEN,
        )
        completed_dfl_app.variation_refuse_reason = "Variation refused."
        completed_dfl_app.save()

        expected_personalisation = default_personalisation() | {
            "reference": completed_dfl_app.reference,
            "reason": "Variation refused.",
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_dfl_app, get_importer_site_domain()),
            "icms_url": get_importer_site_domain(),
        }
        emails.send_variation_request_email(
            vr, VariationRequestDescription.REFUSED, completed_dfl_app
        )
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.importer_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    def test_send_firearms_supplementary_report_email(self, completed_dfl_app):
        exp_template_id = str(
            EmailTemplate.objects.get(
                name=EmailTypes.FIREARMS_SUPPLEMENTARY_REPORT
            ).gov_notify_template_id
        )

        expected_personalisation = default_personalisation() | {
            "reference": completed_dfl_app.reference,
            "validate_digital_signatures_url": get_validate_digital_signatures_url(full_url=True),
            "application_url": get_case_view_url(completed_dfl_app, get_importer_site_domain()),
            "icms_url": get_importer_site_domain(),
        }
        emails.send_firearms_supplementary_report_email(completed_dfl_app)
        assert self.mock_gov_notify_client.send_email_notification.call_count == 1
        self.mock_gov_notify_client.send_email_notification.assert_any_call(
            self.importer_user.email,
            exp_template_id,
            personalisation=expected_personalisation,
        )

    @mock.patch("web.mail.emails.send_application_extension_complete_email")
    @mock.patch("web.mail.emails.send_application_variation_complete_email")
    @mock.patch("web.mail.emails.send_application_complete_email")
    def test_send_completed_application_email_no_variations(
        self,
        mock_send_application_complete_email,
        mock_send_application_variation_complete_email,
        mock_send_application_extension_complete_email,
        completed_cfs_app,
    ):
        mock_send_application_variation_complete_email.return_value = None
        mock_send_application_extension_complete_email.return_value = None
        mock_send_application_complete_email.return_value = None
        emails.send_completed_application_email(completed_cfs_app)
        assert mock_send_application_complete_email.called is True
        assert mock_send_application_extension_complete_email.called is False
        assert mock_send_application_variation_complete_email.called is False

    @mock.patch("web.mail.emails.send_application_extension_complete_email")
    @mock.patch("web.mail.emails.send_application_variation_complete_email")
    @mock.patch("web.mail.emails.send_application_complete_email")
    def test_send_completed_application_extension_process_email(
        self,
        mock_send_application_complete_email,
        mock_send_application_variation_complete_email,
        mock_send_application_extension_complete_email,
        completed_cfs_app,
    ):
        add_variation_request_to_app(
            completed_cfs_app,
            self.ilb_admin_user,
            status=VariationRequest.Statuses.ACCEPTED,
            extension_flag=True,
        )

        mock_send_application_variation_complete_email.return_value = None
        mock_send_application_extension_complete_email.return_value = None
        mock_send_application_complete_email.return_value = None
        emails.send_completed_application_email(completed_cfs_app)
        assert mock_send_application_complete_email.called is False
        assert mock_send_application_extension_complete_email.called is True
        assert mock_send_application_variation_complete_email.called is False

    @mock.patch("web.mail.emails.send_application_extension_complete_email")
    @mock.patch("web.mail.emails.send_application_variation_complete_email")
    @mock.patch("web.mail.emails.send_application_complete_email")
    def test_send_completed_application_variation_process_email(
        self,
        mock_send_application_complete_email,
        mock_send_application_variation_complete_email,
        mock_send_application_extension_complete_email,
        completed_cfs_app,
    ):
        add_variation_request_to_app(
            completed_cfs_app, self.ilb_admin_user, status=VariationRequest.Statuses.ACCEPTED
        )

        mock_send_application_variation_complete_email.return_value = None
        mock_send_application_extension_complete_email.return_value = None
        mock_send_application_complete_email.return_value = None
        emails.send_completed_application_email(completed_cfs_app)
        assert mock_send_application_complete_email.called is False
        assert mock_send_application_extension_complete_email.called is False
        assert mock_send_application_variation_complete_email.called is True

    @mock.patch("web.notify.notify.send_constabulary_deactivated_firearms_notification")
    @mock.patch("web.mail.emails.send_firearms_supplementary_report_email")
    @mock.patch("web.mail.emails.send_completed_application_email")
    def test_send_completed_application_process_notifications_sil(
        self, app_approved_mock, supplementary_report_mock, constabulary_mock, completed_sil_app
    ):
        app = completed_sil_app
        emails.send_completed_application_process_notifications(app)

        app_approved_mock.assert_called_with(app)
        supplementary_report_mock.assert_called_with(app)
        constabulary_mock.assert_not_called()

    @mock.patch("web.notify.notify.send_constabulary_deactivated_firearms_notification")
    @mock.patch("web.mail.emails.send_firearms_supplementary_report_email")
    @mock.patch("web.mail.emails.send_completed_application_email")
    def test_send_completed_application_process_notifications_dfl(
        self, app_approved_mock, supplementary_report_mock, constabulary_mock, completed_dfl_app
    ):
        app = completed_dfl_app
        emails.send_completed_application_process_notifications(app)

        app_approved_mock.assert_called_with(app)
        supplementary_report_mock.assert_called_with(app)
        constabulary_mock.assert_called_with(app)
