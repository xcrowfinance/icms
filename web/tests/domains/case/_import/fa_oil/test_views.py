import pytest
from django.urls import reverse
from pytest_django.asserts import assertInHTML, assertRedirects

from web.domains.case.services import document_pack
from web.models import (
    ImportApplicationLicence,
    ImportApplicationType,
    OpenIndividualLicenceApplication,
    Task,
)
from web.tests.auth import AuthTestCase
from web.tests.domains.case._import.factory import OILApplicationFactory
from web.tests.flow.factories import TaskFactory

LOGIN_URL = "/"


class TestImportAppplicationCreateView(AuthTestCase):
    url = "/import/create/firearms/oil/"
    redirect_url = f"{LOGIN_URL}?next={url}"

    def test_anonymous_access_redirects(self):
        response = self.anonymous_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, self.redirect_url)

    def test_forbidden_access(self):
        response = self.exporter_client.get(self.url)
        assert response.status_code == 403

    def test_create_ok(self):
        response = self.importer_client.get(self.url)
        assert response.status_code == 200

        response = self.importer_client.post(
            reverse("import:create-fa-oil"),
            data={"importer": self.importer.pk, "importer_office": self.importer_office.pk},
        )
        assert response.status_code == 302

        application = OpenIndividualLicenceApplication.objects.get(importer_id=self.importer.pk)
        assert application.process_type == OpenIndividualLicenceApplication.PROCESS_TYPE

        application_type = application.application_type
        assert application_type.type == ImportApplicationType.Types.FIREARMS
        assert application_type.sub_type == ImportApplicationType.SubTypes.OIL

        task = application.tasks.get()
        assert task.task_type == Task.TaskType.PREPARE
        assert task.is_active is True

    def test_create_missing_office(self):
        response = self.importer_client.get(self.url)
        assert response.status_code == 200

        response = self.importer_client.post(
            reverse("import:create-fa-oil"), data={"importer": self.importer.pk}
        )
        assert response.status_code == 200
        assertInHTML(
            '<div class="error-message">You must enter this item', response.content.decode("utf-8")
        )

    def test_anonymous_post_access_redirects(self):
        response = self.anonymous_client.post(self.url)
        assert response.status_code == 302

    def test_forbidden_post_access(self):
        response = self.exporter_client.post(self.url)
        assert response.status_code == 403


@pytest.mark.django_db
def test_take_ownership(importer_one_main_contact, importer, icms_admin_client):
    process = OILApplicationFactory.create(
        status="SUBMITTED",
        importer=importer,
        created_by=importer_one_main_contact,
        last_updated_by=importer_one_main_contact,
    )
    TaskFactory.create(process=process, task_type=Task.TaskType.PROCESS)
    oil_app = process.get_specific_model()
    oil_app.licences.create()

    response_workbasket = icms_admin_client.get("/workbasket/")
    assert "Take Ownership" in response_workbasket.content.decode()

    # After taking ownership we now navigate to the case management "view application" view.
    response = icms_admin_client.post(
        f"/case/import/{process.pk}/admin/take-ownership/", follow=True
    )

    assert response.status_code == 200
    view_application_response = response.content.decode()
    assert "Firearms and Ammunition (Open Individual Import Licence)" in view_application_response


@pytest.mark.django_db
def test_release_ownership(
    test_icms_admin_user, icms_admin_client, importer, importer_one_main_contact
):
    process = OILApplicationFactory.create(
        status="SUBMITTED",
        importer=importer,
        created_by=importer_one_main_contact,
        last_updated_by=importer_one_main_contact,
        case_owner=test_icms_admin_user,
    )
    TaskFactory.create(process=process, task_type=Task.TaskType.PROCESS)

    response = icms_admin_client.post(
        f"/case/import/{process.pk}/admin/release-ownership/", follow=True
    )

    assert "Manage" in response.content.decode()


@pytest.mark.django_db
def test_close_case(test_icms_admin_user, icms_admin_client, importer, importer_one_main_contact):
    process = OILApplicationFactory.create(
        status="SUBMITTED",
        importer=importer,
        created_by=importer_one_main_contact,
        last_updated_by=importer_one_main_contact,
        case_owner=test_icms_admin_user,
    )
    task = TaskFactory.create(process=process, task_type=Task.TaskType.PROCESS)
    licence = document_pack.pack_draft_create(process)

    icms_admin_client.post(
        f"/case/import/{process.pk}/admin/manage/", data={"send_email": True}, follow=True
    )

    process.refresh_from_db()
    assert process.status == "STOPPED"

    licence.refresh_from_db()
    assert licence.status == document_pack.PackStatus.ARCHIVED

    task.refresh_from_db()
    assert task.is_active is False


def test_fa_oil_app_submitted_has_a_licence(fa_oil_app_submitted):
    assert fa_oil_app_submitted.licences.filter(
        status=ImportApplicationLicence.Status.DRAFT
    ).exists()
