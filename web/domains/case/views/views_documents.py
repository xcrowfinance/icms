from typing import Any

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import QuerySet
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from guardian.shortcuts import get_objects_for_user

from web.domains.case.types import DocumentPack
from web.domains.case.utils import get_case_page_title
from web.flow.models import ProcessTypes as pt
from web.mail.url_helpers import get_constabulary_document_download_view_url
from web.models import (
    CaseDocumentReference,
    Constabulary,
    ImportApplication,
    ImportApplicationLicence,
)
from web.permissions import Perms
from web.utils.s3 import get_file_from_s3


class BaseConstabularyDocumentView(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = [Perms.page.view_documents_constabulary]

    def has_permission(self) -> bool:
        has_required_permissions = super().has_permission()
        if not has_required_permissions:
            return False

        constabularies: QuerySet[Constabulary] = get_objects_for_user(
            self.request.user,
            [Perms.obj.constabulary.verified_fa_authority_editor],
            Constabulary.objects.filter(is_active=True),
        )
        if constabularies:
            return self.is_application_linked_to_constabularies(constabularies)
        return False

    def is_application_linked_to_constabularies(
        self, constabularies: QuerySet[Constabulary]
    ) -> bool:
        application = self.get_object().get_specific_model()
        match application.process_type:
            case pt.FA_DFL:
                return application.constabulary in constabularies
            case _:
                return False

    def get_document_pack(self, application) -> DocumentPack:
        return get_object_or_404(application.licences, pk=self.kwargs["doc_pack_pk"])


class ConstabularyDocumentView(BaseConstabularyDocumentView, DetailView):
    template_name = "web/domains/case/view-case-documents.html"
    model = ImportApplication
    pk_url_kwarg = "application_pk"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        application = self.object.get_specific_model()
        case_type = "import"
        context["page_title"] = get_case_page_title(case_type, application, "Issued Documents")
        context["process"] = application
        context["case_type"] = case_type
        context["org"] = application.importer
        return context | self.get_document_context_data(application)

    def get_licence_cdr(self, issued_document: ImportApplicationLicence) -> CaseDocumentReference:
        return get_object_or_404(
            issued_document.document_references, document_type=CaseDocumentReference.Type.LICENCE
        )

    def get_cover_letter_cdr(
        self, issued_document: ImportApplicationLicence
    ) -> CaseDocumentReference:
        return get_object_or_404(
            issued_document.document_references,
            document_type=CaseDocumentReference.Type.COVER_LETTER,
        )

    def get_document_context_data(self, application: ImportApplication) -> dict[str, Any]:
        at = application.application_type
        doc_pack = self.get_document_pack(application)
        licence_cdr = self.get_licence_cdr(doc_pack)
        cover_letter_cdr = self.get_cover_letter_cdr(doc_pack)
        return {
            "issue_date": doc_pack.case_completion_datetime,
            "is_import": True,
            "document_reference": application.reference,
            "type_label": at.get_type_display(),
            "licence_url": get_constabulary_document_download_view_url(
                application, doc_pack, licence_cdr
            ),
            "cover_letter_flag": True,
            "cover_letter_url": get_constabulary_document_download_view_url(
                application, doc_pack, cover_letter_cdr
            ),
        }


class ConstabularyDocumentDownloadView(BaseConstabularyDocumentView, DetailView):
    model = ImportApplication
    pk_url_kwarg = "application_pk"

    def has_permission(self) -> bool:
        has_required_permissions = super().has_permission()
        if not has_required_permissions:
            return False
        application = self.get_object().get_specific_model()
        doc_pack = self.get_document_pack(application)
        if doc_pack and self.kwargs["cdr_pk"] in doc_pack.document_references.values_list(
            "pk", flat=True
        ):
            return True
        return False

    def get(self, *args, **kwargs) -> HttpResponse:
        cdr = CaseDocumentReference.objects.get(pk=kwargs["cdr_pk"])
        file_content = get_file_from_s3(cdr.document.path)
        response = HttpResponse(content=file_content, content_type=cdr.document.content_type)
        response["Content-Disposition"] = f'attachment; filename="{cdr.document.filename}"'
        return response
