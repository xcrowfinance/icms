from typing import TYPE_CHECKING

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views.generic import DetailView

from web.domains.case.utils import check_application_permission
from web.flow.models import Process, ProcessTypes

if TYPE_CHECKING:
    from web.domains.case._import.models import ImportApplication
    from web.domains.case.export.models import ExportApplication


class CaseHistoryView(PermissionRequiredMixin, LoginRequiredMixin, DetailView):
    """Case management view for viewing application variations."""

    licence_date_format = "%d %b %Y"

    # DetailView config
    model = Process
    pk_url_kwarg = "application_pk"

    def has_permission(self):
        application = self.get_object().get_specific_model()

        try:
            check_application_permission(application, self.request.user, self.kwargs["case_type"])
        except PermissionDenied:
            return False

        return True

    def get_context_data(self, **kwargs):
        application = self.object.get_specific_model()
        case_type = self.kwargs["case_type"]
        base_context = super().get_context_data(**kwargs)

        common_context = {
            # TODO: Fix all management page_title context to be the following
            "page_title": f"Case {application.reference}",
            "application_type": ProcessTypes(application.process_type).label,
            "process": application,
            "case_type": case_type,
            "readonly_view": True,
        }

        if application.is_import_application():
            app_context = self._get_licence_context(application)
        else:
            app_context = self._get_certificate_context(application)

        return base_context | common_context | app_context

    def _get_licence_context(self, application: "ImportApplication"):
        licences = (
            application.licences.filter(case_reference__isnull=False)
            .prefetch_related("document_references")
            .order_by("-created_at")
        )

        return {
            "licences": [
                {
                    "case_reference": lic.case_reference,
                    "variation_request": lic.case_reference.split("/")[3:],
                    "issue_paper_licence_only": lic.issue_paper_licence_only,
                    "licence_start_date": lic.licence_start_date.strftime(self.licence_date_format),
                    "licence_end_date": lic.licence_end_date.strftime(self.licence_date_format),
                    "case_completion_date": lic.case_completion_date.strftime(
                        self.licence_date_format
                    ),
                    "documents": [
                        {
                            "name": doc.get_document_type_display(),
                            "reference": doc.reference,
                            "url": reverse(
                                "case:view-case-document",
                                kwargs={
                                    "application_pk": application.id,
                                    "case_type": "import",
                                    "object_pk": lic.pk,
                                    "casedocumentreference_pk": doc.pk,
                                },
                            ),
                        }
                        for doc in lic.document_references.all()
                    ],
                }
                for lic in licences
            ]
        }

    def _get_certificate_context(self, application: "ExportApplication"):
        return {}

    def get_template_names(self) -> list[str]:
        case_type = self.kwargs["case_type"]

        if case_type == "import":
            return ["web/domains/case/import_licence_history.html"]

        if case_type == "export":
            return ["web/domains/case/export_certificate_history.html"]

        raise NotImplementedError(f"Unknown case_type {case_type}")
