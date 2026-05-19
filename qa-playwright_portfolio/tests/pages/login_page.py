from __future__ import annotations

from playwright.sync_api import Locator, Page, expect


class LoginPage:
    PATH = "/login.html"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url
        self.username_input = page.get_by_test_id("username-input")
        self.password_input = page.get_by_test_id("password-input")
        self.login_button = page.get_by_test_id("login-button")
        self.login_message = page.get_by_test_id("login-message")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}{self.PATH}")
        expect(self.username_input).to_be_visible()

    def login(self, username: str, password: str) -> None:
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()

    def submit_empty_form(self) -> None:
        self.login_button.click()

    def expect_message_contains(self, text: str) -> None:
        expect(self.login_message).to_contain_text(text)

    def expect_redirected_to_upload(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}/upload.html")

    def expect_stays_on_login(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}{self.PATH}")

    def expect_login_button_enabled(self) -> None:
        expect(self.login_button).to_be_enabled()

    def expect_message_state(self, state: str) -> None:
        expect(self.login_message).to_have_attribute("data-state", state)

    def login_message_state(self) -> str | None:
        return self._message_locator().get_attribute("data-state")

    def _message_locator(self) -> Locator:
        return self.login_message
