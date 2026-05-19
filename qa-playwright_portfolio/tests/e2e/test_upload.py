from __future__ import annotations

import time
from uuid import uuid4

from tests.pages.upload_page import UploadPage


def test_upload_success_displays_completed_status(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    upload_page.open()
    upload_page.upload_file(
        file_name=f"sample-{uuid4().hex}.png",
        mime_type="image/png",
        buffer=b"fake-png-content",
    )

    upload_page.expect_status_contains("completed")
    upload_page.expect_status_state("success")
    upload_page.expect_message_state("success")
    upload_page.expect_upload_button_enabled()


def test_upload_rejects_disallowed_extension_before_submit(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    upload_page.open()
    upload_page.upload_file(
        file_name=f"sample-{uuid4().hex}.exe",
        mime_type="application/octet-stream",
        buffer=b"not-allowed",
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_message_contains(".png")
    upload_page.expect_message_contains(".mp4")
    upload_page.expect_upload_button_enabled()


def test_upload_rejects_duplicate_filename(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)
    duplicate_name = f"repeat-check-{uuid4().hex}.jpg"

    upload_page.open()
    upload_page.upload_file(
        file_name=duplicate_name,
        mime_type="image/jpeg",
        buffer=b"first-upload",
    )

    upload_page.expect_status_contains("completed")
    upload_page.expect_status_state("success")

    upload_page.upload_file(
        file_name=duplicate_name,
        mime_type="image/jpeg",
        buffer=b"second-upload",
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_upload_button_enabled()


def test_upload_rejects_submit_without_file(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    upload_page.open()
    upload_page.submit_without_file()

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_upload_button_enabled()


def test_upload_marks_processing_failure_as_error(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    upload_page.open()
    upload_page.upload_file(
        file_name=f"status-fail-{uuid4().hex}.png",
        mime_type="image/png",
        buffer=b"processing-failure",
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_status_contains("failed")
    upload_page.expect_upload_button_enabled()


def test_upload_handles_status_lookup_server_error(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    page.route(
        "**/upload-status/*",
        lambda route: route.fulfill(
            status=500,
            content_type="application/json",
            body='{"detail":"status lookup failed"}',
        ),
    )

    upload_page.open()
    upload_page.upload_file(
        file_name=f"status-error-{uuid4().hex}.png",
        mime_type="image/png",
        buffer=b"status-error",
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_message_contains("status lookup failed")
    upload_page.expect_upload_button_enabled()

    page.unroute("**/upload-status/*")


def test_upload_handles_network_error_during_log_creation(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    page.route("**/upload-log", lambda route: route.abort("failed"))

    upload_page.open()
    upload_page.upload_file(
        file_name=f"log-network-{uuid4().hex}.png",
        mime_type="image/png",
        buffer=b"log-network-error",
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_upload_button_enabled()

    page.unroute("**/upload-log")


def test_upload_shows_loading_during_slow_status_lookup(page, app_base_url: str) -> None:
    upload_page = UploadPage(page, app_base_url)

    def delay_status_lookup(route) -> None:
        time.sleep(1)
        route.continue_()

    page.route("**/upload-status/*", delay_status_lookup)

    upload_page.open()
    upload_page.upload_file(
        file_name=f"slow-status-{uuid4().hex}.png",
        mime_type="image/png",
        buffer=b"slow-status",
    )

    upload_page.expect_message_state("loading")
    upload_page.expect_status_state("success")
    upload_page.expect_message_state("success")
    upload_page.expect_upload_button_enabled()

    page.unroute("**/upload-status/*")
