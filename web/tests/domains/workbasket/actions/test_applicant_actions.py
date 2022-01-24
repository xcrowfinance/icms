import pytest
from django.utils import timezone

from web.domains.case._import.wood.models import WoodQuotaApplication
from web.domains.case.models import VariationRequest
from web.domains.case.shared import ImpExpStatus
from web.domains.user.models import User
from web.domains.workbasket.actions.applicant_actions import (
    SubmitVariationUpdateAction,
    ViewApplicationAction,
)
from web.domains.workbasket.actions.shared_actions import ClearApplicationAction
from web.flow.models import Task


class TestApplicantActions:
    user: User
    app: WoodQuotaApplication
    TT = Task.TaskType
    ST = ImpExpStatus

    @pytest.fixture(autouse=True)
    def setup(self, test_import_user):
        self.user = test_import_user

        # set pk as it's the minimum needed to craft the url
        self.app = WoodQuotaApplication(pk=1)

    def test_view_application_action_is_shown(self):
        # setup
        active_tasks = []

        # Statuses when the View Application link should show
        shown_statuses = [
            self.ST.SUBMITTED,
            self.ST.PROCESSING,
            self.ST.VARIATION_REQUESTED,
            self.ST.COMPLETED,
        ]

        for status in self.ST:
            self.app.status = status

            # test
            action = ViewApplicationAction(self.user, "import", self.app, active_tasks, False, True)

            if status in shown_statuses:
                assert action.show_link()
                wb_action = action.get_workbasket_actions()[0]
                assert wb_action.name == "View Application"

            else:
                assert not action.show_link()

    def test_submit_variation_request_update_action_is_shown(self, wood_app_submitted):
        # setup
        wood_app_submitted.variation_requests.create(
            status=VariationRequest.OPEN,
            what_varied="Dummy what_varied",
            why_varied="Dummy why_varied",
            when_varied=timezone.now().date(),
            requested_by=self.user,
        )
        wood_app_submitted.status = self.ST.VARIATION_REQUESTED
        active_tasks = [self.TT.VR_REQUEST_CHANGE]

        # test
        action = SubmitVariationUpdateAction(
            self.user, "import", wood_app_submitted, active_tasks, False, True
        )
        assert action.show_link()

        wb_action = action.get_workbasket_actions()[0]
        assert wb_action.name == "Submit Update"

    def test_submit_variation_request_update_action_not_shown(self):
        # setup
        self.app.status = self.ST.VARIATION_REQUESTED
        active_tasks = []

        action = SubmitVariationUpdateAction(
            self.user, "import", self.app, active_tasks, False, True
        )
        assert not action.show_link()

    def test_clear_application_action_is_shown(self, test_icms_admin_user):
        active_tasks = []
        for status in self.ST:
            self.app.status = status

            # test
            action = ClearApplicationAction(
                self.user, "import", self.app, active_tasks, False, True
            )

            if status == self.ST.COMPLETED:
                assert action.show_link()
                wb_action = action.get_workbasket_actions()[0]
                assert wb_action.name == "Clear"

            else:
                assert not action.show_link()

    def test_acknowledge_complete_notification_is_shown(self, wood_app_submitted):
        ...