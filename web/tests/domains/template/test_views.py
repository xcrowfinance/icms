import pytest
from pytest_django.asserts import assertInHTML, assertRedirects

from web.tests.auth import AuthTestCase
from web.tests.conftest import LOGIN_URL

from .factory import TemplateFactory


class TestTemplateListView(AuthTestCase):
    url = "/template/"
    redirect_url = f"{LOGIN_URL}?next={url}"

    def test_anonymous_access_redirects(self):
        response = self.anonymous_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, self.redirect_url)

    def test_forbidden_access(self):
        response = self.importer_client.get(self.url)
        assert response.status_code == 403

    def test_authorized_access(self):
        response = self.ilb_admin_client.get(self.url)
        assert response.status_code == 200

    def test_page_title(self):
        response = self.ilb_admin_client.get(self.url)
        assert response.context_data["page_title"] == "Maintain Templates"

    def test_number_of_pages(self):
        TemplateFactory.create_batch(118, is_active=True)

        response = self.ilb_admin_client.get(self.url, {"template_name": ""})
        page = response.context_data["page"]
        assert page.paginator.num_pages == 5

    def test_page_results(self):
        TemplateFactory.create_batch(103, is_active=True)

        response = self.ilb_admin_client.get(self.url, {"page": "3", "template_name": ""})
        page = response.context_data["page"]
        assert len(page.object_list) == 50


class TestEndorsementCreateView(AuthTestCase):
    url = "/template/endorsement/new/"
    redirect_url = f"{LOGIN_URL}?next={url}"

    def test_anonymous_access_redirects(self):
        response = self.anonymous_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, self.redirect_url)

    def test_forbidden_access(self):
        response = self.importer_client.get(self.url)
        assert response.status_code == 403

    def test_authorized_access(self):
        response = self.ilb_admin_client.get(self.url)
        assert response.status_code == 200

    def test_page_title(self):
        response = self.ilb_admin_client.get(self.url)
        assert response.context_data["page_title"] == "New Endorsement"


class TestTemplateEditView(AuthTestCase):
    @pytest.fixture(autouse=True)
    def setup(self, _setup):
        self.template = TemplateFactory()
        self.url = f"/template/{self.template.id}/edit/"
        self.redirect_url = f"{LOGIN_URL}?next={self.url}"

    def test_anonymous_access_redirects(self):
        response = self.anonymous_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, self.redirect_url)

    def test_forbidden_access(self):
        response = self.importer_client.get(self.url)
        assert response.status_code == 403

    def test_authorized_access(self):
        response = self.ilb_admin_client.get(self.url)
        assert response.status_code == 200

    def test_page_title(self):
        response = self.ilb_admin_client.get(self.url)
        assertInHTML(f"Editing {self.template}", response.content.decode())


class TestTemplateDetailView(AuthTestCase):
    @pytest.fixture(autouse=True)
    def setup(self, _setup):
        self.template = TemplateFactory()
        self.url = f"/template/{self.template.id}/"
        self.redirect_url = f"{LOGIN_URL}?next={self.url}"

    def test_anonymous_access_redirects(self):
        response = self.anonymous_client.get(self.url)
        assert response.status_code == 302
        assertRedirects(response, self.redirect_url)

    def test_forbidden_access(self):
        response = self.importer_client.get(self.url)
        assert response.status_code == 403

    def test_authorized_access(self):
        response = self.ilb_admin_client.get(self.url)
        assert response.status_code == 200

    def test_page_title(self):
        response = self.ilb_admin_client.get(self.url)
        assertInHTML(f"Viewing {self.template}", response.content.decode())
