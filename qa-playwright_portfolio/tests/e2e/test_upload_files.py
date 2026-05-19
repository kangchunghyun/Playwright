from __future__ import annotations

import mimetypes
from pathlib import Path
from uuid import uuid4

import pytest

from tests.pages.upload_page import UploadPage


TEST_DATA_DIR = Path(__file__).resolve().parents[2] / "test-data"
VALID_DATA_DIR = TEST_DATA_DIR / "valid"
INVALID_DATA_DIR = TEST_DATA_DIR / "invalid"
ALLOWED_EXTENSIONS = {".tif", ".tiff", ".jp2", ".jpg", ".jpeg", ".png", ".mp4"}


def discover_sample_files(directory: Path) -> list[Path]:
    return sorted(
        file_path
        for file_path in directory.iterdir()
        if file_path.is_file() and file_path.name != ".gitkeep"
    )


VALID_UPLOAD_FILES = discover_sample_files(VALID_DATA_DIR)
INVALID_UPLOAD_FILES = discover_sample_files(INVALID_DATA_DIR)


def build_unique_upload_name(file_path: Path) -> str:
    return f"{file_path.stem}-{uuid4().hex}{file_path.suffix}"


def resolve_mime_type(file_path: Path) -> str:
    mime_type, _ = mimetypes.guess_type(file_path.name)
    return mime_type or "application/octet-stream"


def assert_sample_directory_rule(file_path: Path, expected_kind: str) -> None:
    is_allowed_extension = file_path.suffix.lower() in ALLOWED_EXTENSIONS

    if expected_kind == "valid" and not is_allowed_extension:
        pytest.fail(
            "Sample classification mismatch: "
            f"`{file_path.name}` is under `test-data/valid` but its extension "
            f"`{file_path.suffix}` is not in the allowed set {sorted(ALLOWED_EXTENSIONS)}."
        )

    if expected_kind == "invalid" and is_allowed_extension:
        pytest.fail(
            "Sample classification mismatch: "
            f"`{file_path.name}` is under `test-data/invalid` but its extension "
            f"`{file_path.suffix}` is allowed. Move it to `test-data/valid` if it is expected to pass."
        )


@pytest.mark.parametrize("file_path", VALID_UPLOAD_FILES, ids=lambda path: path.name)
def test_upload_accepts_valid_sample_files(
    page,
    app_base_url: str,
    file_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    upload_page = UploadPage(page, app_base_url)
    upload_name = build_unique_upload_name(file_path)
    request.node._sample_file_kind = "valid"
    request.node._sample_file_path = str(file_path)
    request.node._upload_file_name = upload_name
    assert_sample_directory_rule(file_path, expected_kind="valid")

    upload_page.open()
    upload_page.upload_file(
        file_name=upload_name,
        mime_type=resolve_mime_type(file_path),
        buffer=file_path.read_bytes(),
    )

    upload_page.expect_status_contains("completed")
    upload_page.expect_status_state("success")
    upload_page.expect_message_state("success")
    upload_page.expect_upload_button_enabled()


@pytest.mark.parametrize("file_path", INVALID_UPLOAD_FILES, ids=lambda path: path.name)
def test_upload_rejects_invalid_sample_files(
    page,
    app_base_url: str,
    file_path: Path,
    request: pytest.FixtureRequest,
) -> None:
    upload_page = UploadPage(page, app_base_url)
    request.node._sample_file_kind = "invalid"
    request.node._sample_file_path = str(file_path)
    request.node._upload_file_name = file_path.name
    assert_sample_directory_rule(file_path, expected_kind="invalid")

    upload_page.open()
    upload_page.upload_file(
        file_name=file_path.name,
        mime_type=resolve_mime_type(file_path),
        buffer=file_path.read_bytes(),
    )

    upload_page.expect_status_state("error")
    upload_page.expect_message_state("error")
    upload_page.expect_upload_button_enabled()
