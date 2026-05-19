import asyncio

from fastapi import APIRouter, File, Form, Query, UploadFile

from server.models.schemas import (
    LoginRequest,
    LoginResponse,
    UploadLogRequest,
    UploadLogResponse,
    UploadResponse,
    UploadStatusResponse,
)
from server.services.mock_service import mock_qa_service


router = APIRouter()


async def apply_optional_delay(scenario: str | None) -> None:
    if scenario == "timeout":
        await asyncio.sleep(5)


@router.post("/login", response_model=LoginResponse)
async def login(
    payload: LoginRequest,
    scenario: str | None = Query(default=None),
) -> dict[str, str | bool]:
    await apply_optional_delay(scenario)
    return mock_qa_service.login(payload.username, payload.password, scenario)


@router.post("/upload-log", response_model=UploadLogResponse)
async def create_upload_log(
    payload: UploadLogRequest,
    scenario: str | None = Query(default=None),
) -> dict[str, str]:
    await apply_optional_delay(scenario)
    return mock_qa_service.create_upload_log(payload.requestedAt, scenario)


@router.post("/upload", response_model=UploadResponse)
async def upload(
    uploadId: str = Form(...),
    file: UploadFile = File(...),
    scenario: str | None = Query(default=None),
) -> dict[str, str]:
    await apply_optional_delay(scenario)
    return await mock_qa_service.upload_file(uploadId, file, scenario)


@router.get("/upload-status/{upload_id}", response_model=UploadStatusResponse)
async def get_upload_status(
    upload_id: str,
    scenario: str | None = Query(default=None),
) -> dict[str, str]:
    await apply_optional_delay(scenario)
    return mock_qa_service.get_upload_status(upload_id, scenario)


@router.post("/test/reset")
async def reset_test_state() -> dict[str, bool]:
    return mock_qa_service.reset_state()
