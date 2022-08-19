from django.db.models import Q

from data_migration.models import Process
from web.models import Task


class TaskBase:
    TASK_TYPE: str = ""

    @classmethod
    def task_batch(cls) -> list[Task]:
        """Prepare Task objects to be created with bulk_create"""

        return [
            Task(**{"process_id": pk, "task_type": cls.TASK_TYPE}) for pk in cls.get_process_pks()
        ]

    @staticmethod
    def get_process_pks() -> list[int]:
        """Return a list of all process pks that require the TASK_TYPE"""

        raise NotImplementedError("Must be implemented on the child class")


class PrepareTask(TaskBase):
    TASK_TYPE = Task.TaskType.PREPARE

    @staticmethod
    def get_process_pks() -> list[int]:
        # TODO: Extend to include other process children (e.g FIR)
        pks = Process.objects.filter(
            Q(importapplication__status="IN_PROGRESS") | Q(exportapplication__status="IN_PROGRESS")
        ).values_list("pk", flat=True)

        return pks


class ProcessTask(TaskBase):
    TASK_TYPE = Task.TaskType.PROCESS

    @staticmethod
    def get_process_pks() -> list[int]:
        # TODO: Extend to include other process children (e.g. FIR)
        # TODO: Refine to not overlap with other tasks (e.g authorise, chief_wait)
        pks = Process.objects.filter(
            Q(importapplication__status__in=["SUBMITTED", "PROCESSING"])
            | Q(exportapplication__status__in=["SUBMITTED", "PROCESSING"])
        ).values_list("pk", flat=True)

        return pks
