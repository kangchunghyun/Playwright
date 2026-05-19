from __future__ import annotations

import json
import shutil
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import Request, urlopen

import pytest
from playwright.sync_api import Browser, BrowserContext, ConsoleMessage, Page, Playwright, sync_playwright

from tests.utils.config import get_api_base_url, get_app_base_url


ARTIFACTS_DIR = Path(__file__).resolve().parents[1] / ".artifacts"
SCREENSHOTS_DIR = ARTIFACTS_DIR / "screenshots"
TRACES_DIR = ARTIFACTS_DIR / "traces"
VIDEOS_DIR = ARTIFACTS_DIR / "videos"
LOGS_DIR = ARTIFACTS_DIR / "logs"


def ensure_artifact_directories() -> None:
    for directory in (SCREENSHOTS_DIR, TRACES_DIR, VIDEOS_DIR, LOGS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def sanitize_node_id(node_id: str) -> str:
    sanitized = []
    for character in node_id:
        if character.isalnum() or character in {"-", "_"}:
            sanitized.append(character)
        else:
            sanitized.append("_")
    return "".join(sanitized).strip("_")


def write_log_file(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo[None]):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(scope="session")
def app_base_url() -> str:
    return get_app_base_url()


@pytest.fixture(scope="session")
def api_base_url() -> str:
    return get_api_base_url()


@pytest.fixture(scope="session")
def playwright_instance() -> Playwright:
    ensure_artifact_directories()
    with sync_playwright() as playwright:
        yield playwright


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Browser:
    browser = playwright_instance.chromium.launch(headless=True)
    yield browser
    browser.close()


@pytest.fixture(autouse=True)
def reset_mock_api_state(api_base_url: str) -> None:
    last_error: Exception | None = None

    for _ in range(5):
        request = Request(
            url=f"{api_base_url}/test/reset",
            method="POST",
            headers={"Content-Type": "application/json"},
            data=b"{}",
        )

        try:
            with urlopen(request, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except (ConnectionResetError, OSError, URLError) as error:
            last_error = error
            time.sleep(0.5)
            continue

        if payload.get("reset") is True:
            return

        pytest.fail("Mock API reset endpoint returned an unexpected response.")

    pytest.fail(f"Failed to reset mock API state: {last_error}")


@pytest.fixture
def context(browser: Browser, request: pytest.FixtureRequest) -> BrowserContext:
    ensure_artifact_directories()
    context = browser.new_context(record_video_dir=str(VIDEOS_DIR))
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    request.node._playwright_context = context
    yield context
    context.close()


@pytest.fixture
def page(context: BrowserContext, request: pytest.FixtureRequest) -> Page:
    test_id = sanitize_node_id(request.node.nodeid)
    page = context.new_page()
    console_logs: list[str] = []
    request_failures: list[str] = []
    response_errors: list[str] = []

    def on_console(message: ConsoleMessage) -> None:
        location = message.location
        url = location.get("url", "")
        line_number = location.get("lineNumber", "")
        console_logs.append(f"[{message.type}] {message.text} ({url}:{line_number})")

    def on_request_failed(failed_request) -> None:
        failure = failed_request.failure
        failure_text = failure if isinstance(failure, str) else failure.get("errorText", "unknown")
        request_failures.append(f"{failed_request.method} {failed_request.url} -> {failure_text}")

    def on_response(response) -> None:
        if response.status >= 400:
            response_errors.append(f"{response.status} {response.request.method} {response.url}")

    page.on("console", on_console)
    page.on("requestfailed", on_request_failed)
    page.on("response", on_response)

    yield page

    failed = bool(
        getattr(request.node, "rep_setup", None) and request.node.rep_setup.failed
    ) or bool(
        getattr(request.node, "rep_call", None) and request.node.rep_call.failed
    )

    if failed:
        screenshot_path = SCREENSHOTS_DIR / f"{test_id}.png"
        trace_path = TRACES_DIR / f"{test_id}.zip"
        browser_log_path = LOGS_DIR / f"{test_id}.log"
        page.screenshot(path=str(screenshot_path), full_page=True)
        context.tracing.stop(path=str(trace_path))

        log_lines = [
            f"nodeid: {request.node.nodeid}",
            f"url: {page.url}",
            "",
            "[console]",
            *console_logs,
            "",
            "[requestfailed]",
            *request_failures,
            "",
            "[http>=400]",
            *response_errors,
        ]
        write_log_file(browser_log_path, log_lines)
    else:
        context.tracing.stop()

    video = page.video
    page.close()

    if failed and video is not None:
        recorded_video_path = Path(video.path())
        target_video_path = VIDEOS_DIR / f"{test_id}{recorded_video_path.suffix or '.webm'}"
        if recorded_video_path.exists():
            shutil.move(str(recorded_video_path), str(target_video_path))
    elif not failed and video is not None:
        recorded_video_path = Path(video.path())
        if recorded_video_path.exists():
            recorded_video_path.unlink()
