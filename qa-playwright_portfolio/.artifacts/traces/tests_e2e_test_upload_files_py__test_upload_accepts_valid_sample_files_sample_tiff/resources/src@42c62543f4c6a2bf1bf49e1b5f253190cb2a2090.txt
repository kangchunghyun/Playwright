from __future__ import annotations

from pathlib import Path
from uuid import uuid4

import pytest

from tests.pages.upload_page import UploadPage


TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test-data"

VALID_UPLOAD_FILES = [
    TEST_DATA_DIR / "valid" / "sample.jpg",
    TEST_DATA_DIR / "valid" / "sample.jpeg",
    TEST_DATA_DIR / "valid" / "sample.png",
    TEST_DATA_DIR / "valid" / "sample.tif",
    TEST_DATA_DIR / "valid" / "sample.tiff",
    TEST_DATA_DIR / "valid" / "sample.jp2",
    TEST_DATA_DIR / "valid" / "sample.mp4",
]

INVALID_UPLOAD_FILES = [
    TEST_DATA_DIR / "invalid" / "sample.exe",
    TEST_DATA_DIR / "invalid" / "sample.txt",
    TEST_DATA_DIR / "invalid" / "sample.zip",
]

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".jp2": "image/jp2",
    ".mp4": "video/mp4",
    ".exe": "application/octet-stream",
    ".txt": "text/plain",
    ".zip": "application/zip",
}


def build_unique_upload_name(file_path: Path) -> str:
    return f"{file_path.stem}-{uuid4().hex}{file_path.suffix}"


@pytest.mark.parametrize("file_path", VALID_UPLOAD_FILES, ids=lambda path: path.name)
def test_upload_accepts_valid_sample_files(page, app_base_url: str, file_path: Path) -> None:
    upload_page = UploadPage(page, app_base_url)
    upload_name = build_unique_upload_name(file_path)

    upload_page.open()
    upload_page.upload_file(
        file_name=upload_name,
        mime_type=MIME_TYPES[file_path.suffix],
        buffer=file_path.read_bytes(),
    )

    upload_page.expect_status_contains("completed")
    upload_page.expect_status_state("success")
    upload_page.expect_message_state("success")
    upload_page.expect_upload_button_enabled()


@pytest.mark.parametrize("file_path", INVALID_UPLOAD_FILES, ids=lambda path: path.name)
def test_upload_rejects_invalid_sample_files(page, app_base_url: str, file_path: Path) -> None:
    upload_page = UploadPage(page, app_base_url)

    upload_page.open()
    upload_page.upload_file(
        file_name=file_path.name,
        mime_type=MIME_TYPES[file_path.suffix],
        buffer=file_path.read_bytes(),
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_upload_button_enabled()
