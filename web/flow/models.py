from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone

from . import errors


class ProcessTypes(models.TextChoices):
    """Values for Process.process_type."""

    # import
    DEROGATIONS = ("DerogationsApplication", "Derogation from Sanctions Import Ban")
    FA_DFL = ("DFLApplication", "Firearms and Ammunition (Deactivated Firearms Licence)")
    FA_OIL = (
        "OpenIndividualLicenceApplication",
        "Firearms and Ammunition (Open Individual Import Licence)",
    )
    FA_SIL = ("SILApplication", "Firearms and Ammunition (Specific Individual Import Licence)")
    IRON_STEEL = ("ISQuotaApplication", "Iron and Steel (Quota)")
    OPT = ("OutwardProcessingTradeApplication", "Outward Processing Trade")
    SANCTIONS = ("SanctionsAndAdhocApplication", "Sanctions and Adhoc Licence Application")
    SPS = ("PriorSurveillanceApplication", "Prior Surveillance")
    TEXTILES = ("TextilesApplication", "Textiles (Quota)")
    WOOD = ("WoodQuotaApplication", "Wood (Quota)")

    # export
    COM = ("CertificateOfManufactureApplication", "Certificate of Manufacture")
    CFS = ("CertificateOfFreeSaleApplication", "Certificate of Free Sale")
    GMP = (
        "CertificateofGoodManufacturingPractice",
        "Certificate of Good Manufacturing Practice",
    )

    # Import and Export FIR
    FIR = ("FurtherInformationRequest", "Further Information Requests")

    # Access requests
    IAR = ("ImporterAccessRequest", "Importer Access Request")
    EAR = ("ExporterAccessRequest", "Exporter Access Request")

    # Approval requests
    ExpApprovalReq = ("ExporterApprovalRequest", "Exporter Approval Request")
    ImpApprovalReq = ("ImporterApprovalRequest", "Importer Approval Request")


class Process(models.Model):
    """Base class for all processes."""

    # each final subclass needs to set this for downcasting to work; see
    # get_specific_model. they should also mark themselves with typing.final.
    IS_FINAL = False

    # the default=None is to force all code to set this when creating objects.
    # it will fail when save is called.
    process_type = models.CharField(max_length=50, default=None)

    is_active = models.BooleanField(default=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    # Used to order the workbasket - Changes when a variety of actions are performed
    order_datetime = models.DateTimeField(default=timezone.now)

    def check_expected_status(self, expected_statuses: list[str]) -> None:
        """Check the process has one of the expected statuses."""

        # status is set as a model field on all derived classes
        status: str = self.status  # type: ignore[attr-defined]

        if status not in expected_statuses:
            raise errors.ProcessStateError(f"Process is in the wrong state: {status}")

    def get_task(
        self, expected_state: str | list[str], task_type: str, select_for_update: bool = True
    ) -> "Task":
        """Get the latest active task of the given type attached to this
        process, while also checking the process is in the expected state.

        NOTE: This locks the task row for update, so make sure there is an
        active transaction.

        NOTE: this function only makes sense if there is at most one active task
        of the type. If the process can have multiple active tasks of the same
        type, you cannot use this function.

        Raises an exception if anything goes wrong.
        """

        if not self.is_active:
            raise errors.ProcessInactiveError("Process is not active")

        # status is set as a model field on all derived classes
        status: str = self.status  # type: ignore[attr-defined]

        if isinstance(expected_state, list):
            if status not in expected_state:
                raise errors.ProcessStateError(f"Process is in the wrong state: {status}")
        else:
            if status != expected_state:
                raise errors.ProcessStateError(f"Process is in the wrong state: {status}")

        tasks = self.tasks.filter(is_active=True, task_type=task_type).order_by("created")

        if select_for_update:
            tasks = tasks.select_for_update()

        if len(tasks) != 1:
            raise errors.TaskError(f"Expected one active task, got {len(tasks)}")

        return tasks[0]

    def get_active_tasks(self, select_for_update=True) -> "QuerySet[Task]":
        """Get all active task for current process.

        NOTE: This locks the tasks for update, so make sure there is an
        active transaction.

        Useful when soft deleting a process.
        """

        tasks = self.tasks.filter(is_active=True)

        return tasks.select_for_update() if select_for_update else tasks

    def get_active_task_list(self) -> list[str]:
        return list(self.get_active_tasks(False).values_list("task_type", flat=True))

    def get_specific_model(self) -> "Process":
        """Downcast to specific model class."""

        # if we already have the specific model, just return it
        if self.IS_FINAL:
            return self

        pt = self.process_type

        # importer/exporter access requests
        if pt == ProcessTypes.IAR:
            return self.accessrequest.importeraccessrequest

        elif pt == ProcessTypes.EAR:
            return self.accessrequest.exporteraccessrequest

        # import applications
        elif pt == ProcessTypes.FA_OIL:
            return self.importapplication.openindividuallicenceapplication

        elif pt == ProcessTypes.FA_SIL:
            return self.importapplication.silapplication

        elif pt == ProcessTypes.SANCTIONS:
            return self.importapplication.sanctionsandadhocapplication

        elif pt == ProcessTypes.WOOD:
            return self.importapplication.woodquotaapplication

        elif pt == ProcessTypes.DEROGATIONS:
            return self.importapplication.derogationsapplication

        elif pt == ProcessTypes.FA_DFL:
            return self.importapplication.dflapplication

        elif pt == ProcessTypes.OPT:
            return self.importapplication.outwardprocessingtradeapplication

        elif pt == ProcessTypes.TEXTILES:
            return self.importapplication.textilesapplication

        elif pt == ProcessTypes.SPS:
            return self.importapplication.priorsurveillanceapplication

        elif pt == ProcessTypes.IRON_STEEL:
            return self.importapplication.ironsteelapplication

        # Export applications
        elif pt == ProcessTypes.COM:
            return self.exportapplication.certificateofmanufactureapplication

        elif pt == ProcessTypes.CFS:
            return self.exportapplication.certificateoffreesaleapplication

        elif pt == ProcessTypes.GMP:
            return self.exportapplication.certificateofgoodmanufacturingpracticeapplication

        else:
            raise NotImplementedError(f"Unknown process_type {pt}")

    def update_order_datetime(self) -> None:
        self.order_datetime = timezone.now()


class Task(models.Model):
    """A task. A process can have as many tasks as it wants attached to it, and
    tasks maintain a "previous" link to track the task ordering.

    NOTE: a task can have multiple child tasks, but only one parent task.
    """

    class TaskType(models.TextChoices):
        PREPARE: str = ("prepare", "Prepare")  # type:ignore[assignment]
        PROCESS: str = ("process", "Process")  # type:ignore[assignment]
        VR_REQUEST_CHANGE: str = (
            "vr_request_change",
            "VR_REQUEST_CHANGE",
        )  # type:ignore[assignment]
        AUTHORISE: str = ("authorise", "Authorise")  # type:ignore[assignment]

        DOCUMENT_ERROR: str = ("document_error", "Digital signing error")  # type:ignore[assignment]
        DOCUMENT_SIGNING: str = ("document_signing", "Digital signing")  # type:ignore[assignment]

        CHIEF_WAIT: str = ("chief_wait", "CHIEF_WAIT")  # type:ignore[assignment]
        CHIEF_ERROR: str = ("chief_error", "CHIEF_ERROR")  # type:ignore[assignment]

        REJECTED: str = ("rejected", "Rejected")  # type:ignore[assignment]

    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name="tasks")

    task_type = models.CharField(max_length=30, choices=TaskType.choices)

    is_active = models.BooleanField(default=True, db_index=True)

    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(blank=True, null=True)

    previous = models.ForeignKey("self", related_name="next", null=True, on_delete=models.CASCADE)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        db_index=True,
        on_delete=models.CASCADE,
        related_name="+",
    )

    def __str__(self):
        return f"Task(pk={self.id!r}, task_type={self.task_type!r})"
