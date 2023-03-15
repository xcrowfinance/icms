from django.urls import reverse, reverse_lazy

from web.domains.cat.forms import CATFilter
from web.models import CertificateApplicationTemplate, ExportApplicationType
from web.tests.auth import AuthTestCase


class TestCATListView(AuthTestCase):
    url = reverse_lazy("cat:list")

    def test_template_context(self):
        self.login_with_permissions(["exporter_access"])
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/domains/cat/list.html")
        self.assertIsInstance(response.context["filter"], CATFilter)

    def test_filter_queryset_by_name(self):
        for name in ("Foo", "Bar", "Baz"):
            CertificateApplicationTemplate.objects.create(
                owner=self.user,
                name=name,
                application_type=ExportApplicationType.Types.GMP,
            )

        self.login_with_permissions(["exporter_access"])
        # Filtering with query parameters.
        response = self.client.get(self.url, {"name": "foo"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual([t.name for t in response.context["templates"]], ["Foo"])

    def test_filter_defaults_to_current_templates(self):
        foo = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="foo",
            application_type=ExportApplicationType.Types.GMP,
            is_active=True,
        )
        CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="bar",
            application_type=ExportApplicationType.Types.GMP,
            is_active=False,
        )

        self.login_with_permissions(["exporter_access"])
        response = self.client.get(self.url, {})

        self.assertEqual(response.status_code, 200)
        # The archived template is not shown.
        self.assertEqual([t.pk for t in response.context["templates"]], [foo.pk])


class TestCATCreateView(AuthTestCase):
    def test_can_create_template(self):
        with self.assertRaises(CertificateApplicationTemplate.DoesNotExist):
            CertificateApplicationTemplate.objects.get()

        url = reverse("cat:create")
        data = {
            "name": "Foo name",
            "description": "Foo description",
            "application_type": "CFS",
            "sharing": "private",
        }
        self.login_with_permissions(["exporter_access"])
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/cat/")

        template = CertificateApplicationTemplate.objects.get()
        self.assertEqual(template.name, "Foo name")


class TestCATEditView(AuthTestCase):
    def test_show_edit_form(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
        )
        url = reverse("cat:edit", kwargs={"cat_pk": cat.pk})

        self.login_with_permissions(["exporter_access"])
        response = self.client.get(url)

        assert response.status_code == 200
        self.assertTemplateUsed(response, "web/domains/cat/edit.html")

    def test_permission_denied(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
        )
        url = reverse("cat:edit", kwargs={"cat_pk": cat.pk})

        self.login_with_permissions([])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)


class TestCATEditStepView(AuthTestCase):
    def test_show_edit_step_form(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
        )
        url = reverse("cat:edit-step", kwargs={"cat_pk": cat.pk, "step": "cfs"})

        self.login_with_permissions(["exporter_access"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "web/domains/cat/edit.html")

    def test_step_form_initial_data(self):
        # Does the form for 1 step in a template display the choices from
        # my saved application template?
        initial_data = {"foo": "bar"}

        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
            data=initial_data,
        )
        url = reverse("cat:edit-step", kwargs={"cat_pk": cat.pk, "step": "cfs"})

        self.login_with_permissions(["exporter_access"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial, initial_data)

    def test_submit_step_form_saves_data_in_application_template(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="GMP template",
            application_type=ExportApplicationType.Types.GMP,
            data={},
        )
        url = reverse("cat:edit-step", kwargs={"cat_pk": cat.pk, "step": "gmp"})

        self.login_with_permissions(["exporter_access"])
        response = self.client.post(url, {})

        self.assertEqual(response.status_code, 302)
        cat.refresh_from_db()

        expected = {
            "auditor_accredited": None,
            "auditor_certified": None,
            "contact": None,
            "gmp_certificate_issued": None,
            "is_manufacturer": None,
            "is_responsible_person": None,
            "manufacturer_address": None,
            "manufacturer_address_entry_type": "",
            "manufacturer_country": None,
            "manufacturer_name": None,
            "manufacturer_postcode": None,
            "responsible_person_address": None,
            "responsible_person_address_entry_type": "",
            "responsible_person_country": None,
            "responsible_person_name": None,
            "responsible_person_postcode": None,
        }
        self.assertEqual(cat.data, expected)


class TestCATArchiveView(AuthTestCase):
    def test_archive_a_template(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="GMP template",
            application_type=ExportApplicationType.Types.GMP,
        )
        self.assertTrue(cat.is_active)

        url = reverse("cat:archive", kwargs={"cat_pk": cat.pk})
        self.login_with_permissions(["exporter_access"])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/cat/")

        cat.refresh_from_db()

        self.assertFalse(cat.is_active)

    def test_permission_denied(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
        )
        url = reverse("cat:archive", kwargs={"cat_pk": cat.pk})

        self.login_with_permissions([])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)


class TestCATRestoreView(AuthTestCase):
    def test_restore_a_template(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="GMP template",
            application_type=ExportApplicationType.Types.GMP,
            is_active=False,
        )
        self.assertFalse(cat.is_active)

        url = reverse("cat:restore", kwargs={"cat_pk": cat.pk})
        self.login_with_permissions(["exporter_access"])
        response = self.client.post(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/cat/")

        cat.refresh_from_db()

        self.assertTrue(cat.is_active)

    def test_permission_denied(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
            is_active=False,
        )
        url = reverse("cat:restore", kwargs={"cat_pk": cat.pk})

        self.login_with_permissions([])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 403)


class TestCATReadOnlyView(AuthTestCase):
    def test_show_disabled_form_for_template(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
        )
        url = reverse("cat:view", kwargs={"cat_pk": cat.pk})

        self.login_with_permissions(["exporter_access"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["read_only"])

    def test_show_disabled_form_for_step(self):
        cat = CertificateApplicationTemplate.objects.create(
            owner=self.user,
            name="CFS template",
            application_type=ExportApplicationType.Types.FREE_SALE,
        )
        url = reverse("cat:view-step", kwargs={"cat_pk": cat.pk, "step": "cfs"})

        self.login_with_permissions(["exporter_access"])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["read_only"])
