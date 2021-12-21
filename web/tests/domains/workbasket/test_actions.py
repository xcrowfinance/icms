import pytest
from django.utils import timezone

from web.domains.case._import.wood.models import WoodQuotaApplication
from web.domains.case.models import VariationRequest
from web.domains.case.shared import ImpExpStatus
from web.domains.user.models import User
from web.domains.workbasket.actions import (  # get_workbasket_applicant_actions,
    AuthoriseDocumentsAction,
    CancelAuthorisationAction,
    ManageApplicationAction,
    SubmitVariationUpdateAction,
    TakeOwnershipAction,
    ViewApplicationAction,
    get_workbasket_actions,
)
from web.flow.models import Task


class TestAdminActions:
    user: User
    app: WoodQuotaApplication
    TT = Task.TaskType

    @pytest.fixture(autouse=True)
    def setup(self, test_icms_admin_user):
        self.user = test_icms_admin_user
        # set pk as it's the minimum needed to craft the url
        self.app = WoodQuotaApplication(pk=1)

    def test_authorise_documents_action_is_shown(self):
        # setup
        self.app.status = ImpExpStatus.VARIATION_REQUESTED
        active_tasks = [self.TT.AUTHORISE]

        # test
        action = AuthoriseDocumentsAction(self.user, "import", self.app, active_tasks)
        assert action.show_link()

        wb_action = action.get_workbasket_action()
        assert wb_action.name == "Authorise Documents"

    def test_authorise_documents_action_not_shown(self):
        # setup
        self.app.status = ImpExpStatus.IN_PROGRESS
        active_tasks = [self.TT.PREPARE]
        # test
        action = AuthoriseDocumentsAction(self.user, "import", self.app, active_tasks)
        assert not action.show_link()

    def test_cancel_authorisation_action_is_shown(self):
        # setup
        self.app.status = ImpExpStatus.VARIATION_REQUESTED
        active_tasks = [self.TT.AUTHORISE]

        # test
        action = CancelAuthorisationAction(self.user, "import", self.app, active_tasks)
        assert action.show_link()

        wb_action = action.get_workbasket_action()
        assert wb_action.name == "Cancel Authorisation"

    def test_cancel_authorisation_action_not_shown(self):
        # setup
        self.app.status = ImpExpStatus.IN_PROGRESS
        active_tasks = [self.TT.PREPARE]

        # test
        action = CancelAuthorisationAction(self.user, "import", self.app, active_tasks)
        assert not action.show_link()

    def test_manage_application_action_is_shown(self):
        # setup
        self.app.status = ImpExpStatus.VARIATION_REQUESTED
        self.app.case_owner = self.user
        active_tasks = [self.TT.PROCESS]

        # test
        action = ManageApplicationAction(self.user, "import", self.app, active_tasks)
        assert action.show_link()

        wb_action = action.get_workbasket_action()
        assert wb_action.name == "Manage"

    def test_manage_application_action_not_shown(self):
        # setup (case owner is not set)
        self.app.status = ImpExpStatus.VARIATION_REQUESTED
        self.app.case_owner = None
        active_tasks = [self.TT.PROCESS]

        # test
        action = ManageApplicationAction(self.user, "import", self.app, active_tasks)
        assert not action.show_link()

    def test_take_ownership_action_is_shown(self):
        # setup
        self.app.status = ImpExpStatus.VARIATION_REQUESTED
        self.app.case_owner = None
        active_tasks = []

        # test
        action = TakeOwnershipAction(self.user, "import", self.app, active_tasks)
        assert action.show_link()

        wb_action = action.get_workbasket_action()
        assert wb_action.name == "Take Ownership"

    def test_take_ownership_action_not_shown(self):
        # setup (case owner is not set)
        self.app.status = ImpExpStatus.VARIATION_REQUESTED
        self.app.case_owner = self.user
        active_tasks = []

        # test
        action = TakeOwnershipAction(self.user, "import", self.app, active_tasks)
        assert not action.show_link()

    def test_view_application_action_is_shown(self):
        # setup
        active_tasks = []

        # test
        action = ViewApplicationAction(self.user, "import", self.app, active_tasks)
        assert action.show_link()

        wb_action = action.get_workbasket_action()
        assert wb_action.name == "View"

    def test_get_workbasket_actions(self, test_icms_admin_user):
        user = test_icms_admin_user
        case_type = "import"
        application = WoodQuotaApplication(
            pk=1,
            status=ImpExpStatus.VARIATION_REQUESTED,
        )

        actions = get_workbasket_actions(user, case_type, application)

        names = [a.name for a in actions]

        assert sorted(names) == ["Take Ownership", "View"]


class TestApplicantActions:
    user: User
    app: WoodQuotaApplication
    TT = Task.TaskType

    @pytest.fixture(autouse=True)
    def setup(self, test_import_user):
        self.user = test_import_user

    def test_submit_variation_request_update_action_is_shown(self, wood_app_submitted):
        # setup
        wood_app_submitted.variation_requests.create(
            status=VariationRequest.OPEN,
            what_varied="Dummy what_varied",
            why_varied="Dummy why_varied",
            when_varied=timezone.now().date(),
            requested_by=self.user,
        )
        wood_app_submitted.status = ImpExpStatus.VARIATION_REQUESTED
        active_tasks = [self.TT.VR_REQUEST_CHANGE]

        # test
        action = SubmitVariationUpdateAction(self.user, "import", wood_app_submitted, active_tasks)
        assert action.show_link()

        wb_action = action.get_workbasket_action()
        assert wb_action.name == "Submit Update"

    def test_submit_variation_request_update_action_not_shown(self, wood_app_submitted):
        # setup
        wood_app_submitted.status = ImpExpStatus.VARIATION_REQUESTED
        active_tasks = []

        action = SubmitVariationUpdateAction(self.user, "import", wood_app_submitted, active_tasks)
        assert not action.show_link()
