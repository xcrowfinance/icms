from web.domains.case.types import ImpAccessOrExpAccess, ImpOrExp, ImpOrExpApproval
from web.flow.models import ProcessTypes
from web.models import (
    ExporterApprovalRequest,
    ImporterApprovalRequest,
    VariationRequest,
    WithdrawApplication,
)
from web.notify import notify
from web.notify.email import send_withdrawal_email as notify_send_withdrawal_email

from .messages import (
    AccessRequestClosedEmail,
    AccessRequestEmail,
    ApplicationCompleteEmail,
    ApplicationExtensionCompleteEmail,
    ApplicationReassignedEmail,
    ApplicationRefusedEmail,
    ApplicationStoppedEmail,
    ApplicationVariationCompleteEmail,
    ExporterAccessRequestApprovalOpenedEmail,
    ImporterAccessRequestApprovalOpenedEmail,
    WithdrawalAcceptedEmail,
    WithdrawalOpenedEmail,
)
from .recipients import (
    get_application_contact_email_addresses,
    get_case_officers_email_addresses,
    get_email_addresses_for_users,
    get_ilb_case_officers_email_addresses,
    get_organisation_contact_email_addresses,
)


def send_access_requested_email(access_request: ImpAccessOrExpAccess) -> None:
    recipients = get_ilb_case_officers_email_addresses()
    for recipient in recipients:
        AccessRequestEmail(access_request=access_request, to=[recipient]).send()


def send_access_request_closed_email(access_request: ImpAccessOrExpAccess) -> None:
    recipients = get_email_addresses_for_users([access_request.submitted_by])
    for recipient in recipients:
        AccessRequestClosedEmail(access_request=access_request, to=[recipient]).send()


def send_completed_application_email(application: ImpOrExp) -> None:
    variations = application.variation_requests.filter(
        status__in=[VariationRequest.Statuses.ACCEPTED, VariationRequest.Statuses.CLOSED]
    )

    if variations.filter(extension_flag=True).exists():
        send_application_extension_complete_email(application)
    elif variations.exists():
        send_application_variation_complete_email(application)
    else:
        send_application_complete_email(application)


def send_application_extension_complete_email(application: ImpOrExp) -> None:
    recipients = get_application_contact_email_addresses(application)
    for recipient in recipients:
        ApplicationExtensionCompleteEmail(application=application, to=[recipient]).send()


def send_application_variation_complete_email(application: ImpOrExp) -> None:
    recipients = get_application_contact_email_addresses(application)
    for recipient in recipients:
        ApplicationVariationCompleteEmail(application=application, to=[recipient]).send()


def send_application_complete_email(application: ImpOrExp) -> None:
    recipients = get_application_contact_email_addresses(application)
    for recipient in recipients:
        ApplicationCompleteEmail(application=application, to=[recipient]).send()


def send_completed_application_process_notifications(application: ImpOrExp) -> None:
    if application.process_type == ProcessTypes.FA_DFL:
        # TODO: ICMSLST-2145 Update to use GOV Notify
        notify.send_constabulary_deactivated_firearms_notification(application.dflapplication)

    if application.process_type in [ProcessTypes.FA_DFL, ProcessTypes.FA_OIL, ProcessTypes.FA_SIL]:
        # TODO: ICMSLST-2153 Update to use GOV Notify
        notify.send_supplementary_report_notification(application)

    send_completed_application_email(application)


def send_application_stopped_email(application: ImpOrExp) -> None:
    recipients = get_application_contact_email_addresses(application)
    for recipient in recipients:
        ApplicationStoppedEmail(application=application, to=[recipient]).send()


def send_application_refused_email(application: ImpOrExp) -> None:
    recipients = get_application_contact_email_addresses(application)
    for recipient in recipients:
        ApplicationRefusedEmail(application=application, to=[recipient]).send()


def send_approval_request_opened_email(approval_request: ImpOrExpApproval) -> None:
    if approval_request.access_request.process_type == ProcessTypes.EAR:
        send_exporter_approval_request_opened_email(approval_request)
    else:
        send_importer_approval_request_opened_email(approval_request)


def send_exporter_approval_request_opened_email(approval_request: ExporterApprovalRequest) -> None:
    org = approval_request.access_request.get_specific_model().link
    recipients = get_organisation_contact_email_addresses(org)
    for recipient in recipients:
        ExporterAccessRequestApprovalOpenedEmail(
            approval_request=approval_request, to=[recipient]
        ).send()


def send_importer_approval_request_opened_email(approval_request: ImporterApprovalRequest) -> None:
    org = approval_request.access_request.get_specific_model().link
    recipients = get_organisation_contact_email_addresses(org)
    for recipient in recipients:
        ImporterAccessRequestApprovalOpenedEmail(
            approval_request=approval_request, to=[recipient]
        ).send()


def send_withdrawal_email(withdrawal: WithdrawApplication) -> None:
    if withdrawal.status == WithdrawApplication.Statuses.OPEN:
        send_withdrawal_opened_email(withdrawal)
    elif withdrawal.status == WithdrawApplication.Statuses.ACCEPTED:
        send_withdrawal_accepted_email(withdrawal)
    else:
        notify_send_withdrawal_email(withdrawal)


def send_withdrawal_opened_email(withdrawal: WithdrawApplication) -> None:
    application = withdrawal.export_application or withdrawal.import_application
    recipients = get_case_officers_email_addresses(application.process_type)
    for recipient in recipients:
        WithdrawalOpenedEmail(withdrawal=withdrawal, to=[recipient]).send()


def send_withdrawal_accepted_email(withdrawal: WithdrawApplication) -> None:
    application = withdrawal.export_application or withdrawal.import_application
    recipients = get_application_contact_email_addresses(application)
    for recipient in recipients:
        WithdrawalAcceptedEmail(withdrawal=withdrawal, to=[recipient]).send()


def send_application_reassigned_email(application: ImpOrExp, comment: str) -> None:
    recipients = get_email_addresses_for_users([application.case_owner])
    for recipient in recipients:
        ApplicationReassignedEmail(application=application, comment=comment, to=[recipient]).send()
