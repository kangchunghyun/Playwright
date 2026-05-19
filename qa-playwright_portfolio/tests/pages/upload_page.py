from __future__ import annotations

from pathlib import Path

from playwright.sync_api import Locator, Page, expect


class UploadPage:
    PATH = "/upload.html"

    def __init__(self, page: Page, base_url: str) -> None:
        self.page = page
        self.base_url = base_url
        self.upload_card = page.get_by_test_id("upload-card")
        self.file_input = page.get_by_test_id("file-input")
        self.upload_button = page.get_by_test_id("upload-button")
        self.upload_status = page.get_by_test_id("upload-status")
        self.upload_message = page.get_by_test_id("upload-message")

    def open(self) -> None:
        self.page.goto(f"{self.base_url}{self.PATH}")
        expect(self.upload_card).to_be_visible()

    def expect_opened(self) -> None:
        expect(self.page).to_have_url(f"{self.base_url}{self.PATH}")
        expect(self.upload_card).to_be_visible()
        expect(self.upload_button).to_be_enabled()

    def upload_file(self, file_name: str, mime_type: str, buffer: bytes) -> None:
        self.file_input.set_input_files(
            [
                {
                    "name": file_name,
                    "mimeType": mime_type,
                    "buffer": buffer,
                }
            ]
        )
        self.upload_button.click()

    def upload_file_from_path(self, file_path: str | Path) -> None:
        self.file_input.set_input_files(str(file_path))
        self.upload_button.click()

    def submit_without_file(self) -> None:
        self.upload_button.click()

    def expect_upload_button_enabled(self) -> None:
        expect(self.upload_button).to_be_enabled()

    def expect_status_contains(self, text: str) -> None:
        expect(self.upload_status).to_contain_text(text)

    def expect_message_contains(self, text: str) -> None:
        expect(self.upload_message).to_contain_text(text)

    def expect_status_state(self, state: str) -> None:
        expect(self.upload_status).to_have_attribute("data-state", state)

    def expect_message_state(self, state: str) -> None:
        expect(self.upload_message).to_have_attribute("data-state", state)

    def upload_status_state(self) -> str | None:
        return self._upload_status_locator().get_attribute("data-state")

    def upload_message_state(self) -> str | None:
        return self._upload_message_locator().get_attribute("data-state")

    def _upload_status_locator(self) -> Locator:
        return self.upload_status

    def _upload_message_locator(self) -> Locator:
        return self.upload_message
