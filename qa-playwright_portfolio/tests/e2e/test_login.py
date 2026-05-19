from __future__ import annotations

from tests.pages.login_page import LoginPage
from tests.pages.upload_page import UploadPage


def test_login_success_redirects_to_upload(page, app_base_url: str) -> None:
    login_page = LoginPage(page, app_base_url)
    upload_page = UploadPage(page, app_base_url)

    login_page.open()
    login_page.login("admin", "1234")

    upload_page.expect_opened()


def test_login_rejects_invalid_credentials(page, app_base_url: str) -> None:
    login_page = LoginPage(page, app_base_url)

    login_page.open()
    login_page.login("admin", "wrong-password")

    login_page.expect_message_state("error")
    login_page.expect_stays_on_login()
    login_page.expect_login_button_enabled()


def test_login_rejects_empty_form(page, app_base_url: str) -> None:
    login_page = LoginPage(page, app_base_url)

    login_page.open()
    login_page.submit_empty_form()

    login_page.expect_message_state("error")
    login_page.expect_stays_on_login()
    login_page.expect_login_button_enabled()


def test_login_handles_session_expired_response(page, app_base_url: str) -> None:
    login_page = LoginPage(page, app_base_url)

    login_page.open()
    login_page.login("expired", "1234")

    login_page.expect_message_state("error")
    login_page.expect_stays_on_login()
    login_page.expect_login_button_enabled()


def test_login_handles_server_error_response(page, app_base_url: str) -> None:
    login_page = LoginPage(page, app_base_url)

    login_page.open()
    login_page.login("server-error", "1234")

    login_page.expect_message_state("error")
    login_page.expect_stays_on_login()
    login_page.expect_login_button_enabled()


def test_login_handles_network_error(page, app_base_url: str) -> None:
    login_page = LoginPage(page, app_base_url)

    page.route("**/login", lambda route: route.abort("failed"))

    login_page.open()
    login_page.login("admin", "1234")

    login_page.expect_message_state("error")
    login_page.expect_stays_on_login()
    login_page.expect_login_button_enabled()

    page.unroute("**/login")
