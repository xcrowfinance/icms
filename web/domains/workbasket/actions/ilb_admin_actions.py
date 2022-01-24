from typing import Any

from django.conf import settings
from django.urls import reverse

from web.domains.case.shared import ImpExpStatus
from web.domains.workbasket.base import WorkbasketAction
from web.flow.models import Task

from .base import Action, ActionT

"""Actions that only apply to ilb admin users are added here"""


class TakeOwnershipAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [ImpExpStatus.SUBMITTED, ImpExpStatus.VARIATION_REQUESTED]
        no_case_owner = not self.application.case_owner

        if correct_status and no_case_owner:
            show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()

        return [
            WorkbasketAction(
                is_post=True,
                name="Take Ownership",
                url=reverse("case:take-ownership", kwargs=kwargs),
            )
        ]


class ViewApplicationCaseAction(Action):
    """Case officer "View Case" link"""

    def show_link(self) -> bool:
        show_link = False

        # A freshly submitted application (no case_owner yet)
        if self.status == ImpExpStatus.SUBMITTED and not self.application.case_owner:
            show_link = True

        elif self.status == ImpExpStatus.PROCESSING:
            # An application being processed by another ilb admin
            if not self.is_case_owner():
                show_link = True

            # An authorised application
            elif Task.TaskType.AUTHORISE in self.active_tasks:
                show_link = True

            # App in CHIEF wait state
            elif (
                settings.ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD
                and Task.TaskType.CHIEF_WAIT in self.active_tasks
            ):
                show_link = True

            # App in CHIEF error state
            elif (
                settings.ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD
                and Task.TaskType.CHIEF_ERROR in self.active_tasks
            ):
                show_link = True

        # An application being processed by another ilb admin (via a variation request)
        elif self.status == ImpExpStatus.VARIATION_REQUESTED and not self.is_case_owner():
            show_link = True

        # An application rejected by the current case officer
        elif self.application.is_rejected(self.active_tasks) and self.is_case_owner():
            show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()

        name = "View Case" if self.application.is_rejected(self.active_tasks) else "View"

        return [
            WorkbasketAction(is_post=False, name=name, url=reverse("case:manage", kwargs=kwargs))
        ]


class ManageApplicationAction(Action):
    def show_link(self) -> bool:
        show_link = False

        if self.status == ImpExpStatus.PROCESSING:
            # I think this is a bug, it should check `self.is_case_owner()`
            # It has been copied "as-is" for now
            if Task.TaskType.PROCESS in self.active_tasks:
                show_link = True

        elif self.status == ImpExpStatus.VARIATION_REQUESTED:
            if self.is_case_owner() and Task.TaskType.PROCESS in self.active_tasks:
                show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()
        return [
            WorkbasketAction(
                is_post=False, name="Manage", url=reverse("case:manage", kwargs=kwargs)
            )
        ]


class AuthoriseDocumentsAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [ImpExpStatus.PROCESSING, ImpExpStatus.VARIATION_REQUESTED]
        correct_task = Task.TaskType.AUTHORISE in self.active_tasks

        if correct_status and correct_task:
            show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()

        return [
            WorkbasketAction(
                is_post=False,
                name="Authorise Documents",
                url=reverse("case:authorise-documents", kwargs=kwargs),
            )
        ]


class CancelAuthorisationAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [ImpExpStatus.PROCESSING, ImpExpStatus.VARIATION_REQUESTED]
        correct_task = Task.TaskType.AUTHORISE in self.active_tasks

        if correct_status and correct_task:
            show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()

        return [
            WorkbasketAction(
                is_post=True,
                name="Cancel Authorisation",
                url=reverse("case:cancel-authorisation", kwargs=kwargs),
            )
        ]


class BypassChiefSuccessAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [
            ImpExpStatus.PROCESSING,
            ImpExpStatus.VARIATION_REQUESTED,
        ]
        correct_task = Task.TaskType.CHIEF_WAIT in self.active_tasks
        correct_setting = settings.ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD

        if correct_status and correct_task and correct_setting:
            show_link = True

        return show_link

    def get_kwargs(self) -> dict[str, Any]:
        return {"application_pk": self.application.pk, "chief_status": "success"}

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()

        return [
            WorkbasketAction(
                is_post=True,
                name="(TEST) Bypass CHIEF",
                url=reverse("import:bypass-chief", kwargs=kwargs),
            )
        ]


class BypassChiefFailureAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [
            ImpExpStatus.PROCESSING,
            ImpExpStatus.VARIATION_REQUESTED,
        ]
        correct_task = Task.TaskType.CHIEF_WAIT in self.active_tasks
        correct_setting = settings.ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD

        if correct_status and correct_task and correct_setting:
            show_link = True

        return show_link

    def get_kwargs(self) -> dict[str, Any]:
        return {"application_pk": self.application.pk, "chief_status": "failure"}

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        kwargs = self.get_kwargs()

        return [
            WorkbasketAction(
                is_post=True,
                name="(TEST) Bypass CHIEF induce failure",
                url=reverse("import:bypass-chief", kwargs=kwargs),
            )
        ]


class ChiefMonitorProgressAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [
            ImpExpStatus.PROCESSING,
            ImpExpStatus.VARIATION_REQUESTED,
        ]
        correct_task = Task.TaskType.CHIEF_WAIT in self.active_tasks

        if correct_status and correct_task:
            show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        return [
            WorkbasketAction(
                is_post=True,
                name="Monitor Progress",
                url="#TODO: ICMSLST-812 - Popup showing progress",
            )
        ]


class ChiefShowLicenceDetailsAction(Action):
    def show_link(self) -> bool:
        show_link = False

        correct_status = self.status in [
            ImpExpStatus.PROCESSING,
            ImpExpStatus.VARIATION_REQUESTED,
        ]
        correct_task = Task.TaskType.CHIEF_ERROR in self.active_tasks

        if correct_status and correct_task:
            show_link = True

        return show_link

    def get_workbasket_actions(self) -> list[WorkbasketAction]:
        return [
            WorkbasketAction(
                is_post=True,
                name="Show Licence Details",
                url="#TODO: ICMSLST-812 - CHIEF Dashboard",
            )
        ]


ILB_ADMIN_ACTIONS: list[ActionT] = [
    TakeOwnershipAction,
    ManageApplicationAction,
    AuthoriseDocumentsAction,
    CancelAuthorisationAction,
    BypassChiefSuccessAction,
    BypassChiefFailureAction,
    ChiefMonitorProgressAction,
    ChiefShowLicenceDetailsAction,
    ViewApplicationCaseAction,
]