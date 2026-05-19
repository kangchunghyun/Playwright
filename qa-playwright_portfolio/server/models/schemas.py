from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str


class UploadLogRequest(BaseModel):
    requestedAt: str | None = None


class UploadLogResponse(BaseModel):
    uploadId: str
    status: str
    message: str


class UploadResponse(BaseModel):
    uploadId: str
    filename: str
    status: str
    message: str


class UploadStatusResponse(BaseModel):
    uploadId: str
    status: str
    message: str
