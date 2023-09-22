from http import HTTPStatus
from unittest import mock

import pytest
from django.test import override_settings
from django.urls import reverse, reverse_lazy
from pytest_django.asserts import assertRedirects

from web.one_login.utils import OneLoginConfig
from web.views import views


class TestRedirectBaseDomainView:
    def test_authenticated_redirects_to_workbasket(self, importer_client):
        response = importer_client.get("")
        assertRedirects(response, reverse("workbasket"))

        response = importer_client.get("/")
        assertRedirects(response, reverse("workbasket"))

    def test_non_authenticated_redirects_to_login(self, db, cw_client):
        response = cw_client.get("")
        assertRedirects(response, reverse("login-start"))

        response = cw_client.get("/")
        assertRedirects(response, reverse("login-start"))


@pytest.mark.parametrize(
    ["staff_sso_enabled", "one_login_enabled", "staff_sso_login_url", "one_login_login_url"],
    [
        (False, False, reverse_lazy("accounts:login"), reverse_lazy("accounts:login")),
        (True, False, reverse_lazy("authbroker_client:login"), reverse_lazy("accounts:login")),
        (False, True, reverse_lazy("accounts:login"), reverse_lazy("one_login:login")),
        (
            True,
            True,
            reverse_lazy("authbroker_client:login"),
            reverse_lazy("one_login:login"),
        ),
    ],
)
def test_login_start_view(
    staff_sso_enabled,
    one_login_enabled,
    staff_sso_login_url,
    one_login_login_url,
    db,
    cw_client,
    exp_client,
    imp_client,
):
    with override_settings(
        STAFF_SSO_ENABLED=staff_sso_enabled, GOV_UK_ONE_LOGIN_ENABLED=one_login_enabled
    ):
        response = cw_client.get(reverse("login-start"))

        assert response.status_code == HTTPStatus.OK
        context = response.context
        assert context["auth_login_url"] == staff_sso_login_url

        response = exp_client.get(reverse("login-start"))
        assert response.status_code == HTTPStatus.OK
        context = response.context
        assert context["auth_login_url"] == one_login_login_url

        response = imp_client.get(reverse("login-start"))
        assert response.status_code == HTTPStatus.OK
        context = response.context
        assert context["auth_login_url"] == one_login_login_url


class TestLogoutView:
    @override_settings(AUTHBROKER_URL="https://fake-sso.trade.gov.uk")
    def test_staff_sso_backend_logout(self, cw_client, ilb_admin_user):
        cw_client.force_login(ilb_admin_user, backend="web.auth.backends.ICMSStaffSSOBackend")

        response = cw_client.post(reverse("logout-user"))

        assertRedirects(
            response, "https://fake-sso.trade.gov.uk/logout/", fetch_redirect_response=False
        )
        self._assert_logged_out(cw_client)

    def test_gov_uk_one_login_backend_logout(self, imp_client, importer_one_contact, monkeypatch):
        imp_client.force_login(
            importer_one_contact, backend="web.auth.backends.ICMSGovUKOneLoginBackend"
        )

        one_login_config_mock = mock.create_autospec(spec=OneLoginConfig)
        one_login_config_mock.return_value.end_session_url = "https://fake-one.login.gov.uk/logout/"
        monkeypatch.setattr(views, "OneLoginConfig", one_login_config_mock)

        response = imp_client.post(reverse("logout-user"))

        assertRedirects(
            response, "https://fake-one.login.gov.uk/logout/", fetch_redirect_response=False
        )
        self._assert_logged_out(imp_client)

    def test_django_model_auth_backend_logout(self, imp_client, importer_one_contact):
        imp_client.force_login(
            importer_one_contact, backend="web.auth.backends.ModelAndObjectPermissionBackend"
        )

        response = imp_client.post(reverse("logout-user"))

        assertRedirects(response, reverse("login-start"))
        self._assert_logged_out(imp_client)

    def test_unknown_backend_logout(self, db, cw_client, caplog):
        response = cw_client.post(reverse("logout-user"))

        assertRedirects(response, reverse("login-start"))
        self._assert_logged_out(cw_client)

        assert caplog.messages[0] == "Unknown backend: , defaulting to login_start"

    def _assert_logged_out(self, client):
        response = client.get("")
        assertRedirects(response, reverse("login-start"))
