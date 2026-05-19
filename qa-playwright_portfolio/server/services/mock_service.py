from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import time
from uuid import uuid4

from fastapi import HTTPException, UploadFile, status


ALLOWED_EXTENSIONS = {".tif", ".tiff", ".jp2", ".jpg", ".jpeg", ".png", ".mp4"}


@dataclass
class UploadRecord:
    upload_id: str
    requested_at: str | None
    status: str = "pending"
    message: str = "업로드 로그가 생성되었습니다."
    filename: str | None = None


class MockQaService:
    def __init__(self) -> None:
        self._upload_records: dict[str, UploadRecord] = {}
        self._uploaded_filenames: set[str] = set()

    def reset_state(self) -> dict[str, bool]:
        self._upload_records.clear()
        self._uploaded_filenames.clear()
        return {"reset": True}

    def login(self, username: str, password: str, scenario: str | None = None) -> dict[str, str | bool]:
        if scenario == "server_error" or username == "server-error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="로그인 처리 중 서버 오류가 발생했습니다.",
            )

        if scenario == "session_expired" or username == "expired":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="세션이 만료되었습니다. 다시 로그인해주세요.",
            )

        if username == "admin" and password == "1234":
            return {
                "success": True,
                "message": "로그인에 성공했습니다. 업로드 화면으로 이동합니다.",
            }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 올바르지 않습니다.",
        )

    def create_upload_log(self, requested_at: str | None, scenario: str | None = None) -> dict[str, str]:
        if scenario == "server_error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="업로드 로그 생성에 실패했습니다.",
            )

        upload_id = f"upload-{int(time())}-{uuid4().hex[:8]}"
        record = UploadRecord(upload_id=upload_id, requested_at=requested_at)
        self._upload_records[upload_id] = record

        return {
            "uploadId": upload_id,
            "status": record.status,
            "message": record.message,
        }

    async def upload_file(
        self,
        upload_id: str,
        file: UploadFile,
        scenario: str | None = None,
    ) -> dict[str, str]:
        record = self._upload_records.get(upload_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="유효하지 않은 uploadId입니다.",
            )

        filename = file.filename or "unnamed-file"
        extension = Path(filename).suffix.lower()

        if scenario == "server_error" or "server-error" in filename.lower():
            record.status = "failed"
            record.message = "파일 업로드 중 서버 오류가 발생했습니다."
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=record.message,
            )

        if extension not in ALLOWED_EXTENSIONS:
            record.status = "failed"
            record.message = "허용되지 않은 확장자입니다."
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=record.message,
            )

        if filename.lower() in self._uploaded_filenames or "duplicate" in filename.lower():
            record.status = "failed"
            record.message = "중복 업로드가 감지되었습니다."
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=record.message,
            )

        record.filename = filename

        if scenario == "processing_failed" or "status-fail" in filename.lower():
            record.status = "failed"
            record.message = "업로드는 접수되었지만 후처리 단계에서 실패했습니다."
        else:
            record.status = "completed"
            record.message = "파일 업로드가 완료되었습니다."

        self._uploaded_filenames.add(filename.lower())
        await file.read()

        return {
            "uploadId": upload_id,
            "filename": filename,
            "status": record.status,
            "message": record.message,
        }

    def get_upload_status(self, upload_id: str, scenario: str | None = None) -> dict[str, str]:
        if scenario == "server_error":
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="업로드 상태 조회 중 서버 오류가 발생했습니다.",
            )

        record = self._upload_records.get(upload_id)

        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="업로드 상태를 찾을 수 없습니다.",
            )

        return {
            "uploadId": upload_id,
            "status": record.status,
            "message": record.message,
        }


mock_qa_service = MockQaService()
