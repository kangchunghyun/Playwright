const API_BASE_URL = "http://localhost:8000";
const ALLOWED_EXTENSIONS = [".tif", ".tiff", ".jp2", ".jpg", ".jpeg", ".png", ".mp4"];

document.addEventListener("DOMContentLoaded", () => {
  initializeLoginPage();
  initializeUploadPage();
});

function initializeLoginPage() {
  const loginForm = document.querySelector('[data-testid="login-form"]');

  if (!loginForm) {
    return;
  }

  loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const usernameInput = document.querySelector('[data-testid="username-input"]');
    const passwordInput = document.querySelector('[data-testid="password-input"]');
    const loginButton = document.querySelector('[data-testid="login-button"]');
    const messageElement = document.querySelector('[data-testid="login-message"]');

    const username = usernameInput?.value.trim() ?? "";
    const password = passwordInput?.value ?? "";

    if (!username || !password) {
      setMessage(messageElement, "아이디와 비밀번호를 모두 입력해주세요.", "error");
      return;
    }

    setButtonLoading(loginButton, true, "로그인 중...");
    setMessage(messageElement, "로그인 요청을 보내는 중입니다.", "loading");

    try {
      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await readJsonSafely(response);

      if (!response.ok) {
        const errorMessage = extractErrorMessage(data, "로그인에 실패했습니다.");
        setMessage(messageElement, errorMessage, "error");
        return;
      }

      const successMessage = data.message ?? "로그인에 성공했습니다. 업로드 화면으로 이동합니다.";
      setMessage(messageElement, successMessage, "success");
      window.setTimeout(() => {
        window.location.href = "./upload.html";
      }, 500);
    } catch (_error) {
      setMessage(
        messageElement,
        "로그인 API 호출 중 네트워크 오류가 발생했습니다. 서버 연결을 확인해주세요.",
        "error"
      );
    } finally {
      setButtonLoading(loginButton, false, "Login");
    }
  });
}

function initializeUploadPage() {
  const uploadForm = document.querySelector('[data-testid="upload-form"]');

  if (!uploadForm) {
    return;
  }

  uploadForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const fileInput = document.querySelector('[data-testid="file-input"]');
    const uploadButton = document.querySelector('[data-testid="upload-button"]');
    const statusElement = document.querySelector('[data-testid="upload-status"]');
    const messageElement = document.querySelector('[data-testid="upload-message"]');

    const file = fileInput?.files?.[0];

    if (!file) {
      setMessage(statusElement, "업로드할 파일을 먼저 선택해주세요.", "error");
      setMessage(messageElement, "파일이 선택되지 않아 업로드를 시작하지 않았습니다.", "error");
      return;
    }

    if (!isAllowedFile(file.name)) {
      setMessage(statusElement, "허용되지 않은 확장자입니다.", "error");
      setMessage(
        messageElement,
        `허용 확장자: ${ALLOWED_EXTENSIONS.join(", ")}`,
        "error"
      );
      return;
    }

    setButtonLoading(uploadButton, true, "업로드 중...");
    setMessage(statusElement, "업로드 로그를 생성하는 중입니다.", "loading");
    setMessage(messageElement, `${file.name} 업로드를 준비하고 있습니다.`, "loading");

    try {
      const uploadId = await createUploadLog();
      setMessage(statusElement, `업로드 로그가 생성되었습니다. uploadId: ${uploadId}`, "success");

      setMessage(messageElement, "파일 업로드를 진행하는 중입니다.", "loading");
      await uploadFile(file, uploadId);
      setMessage(messageElement, "파일 업로드가 완료되었습니다. 상태를 조회합니다.", "loading");

      const statusResult = await fetchUploadStatus(uploadId);
      renderUploadStatus(statusElement, messageElement, uploadId, statusResult);
    } catch (error) {
      const resolvedMessage = error instanceof Error ? error.message : "알 수 없는 오류가 발생했습니다.";
      setMessage(statusElement, "업로드 흐름이 중단되었습니다.", "error");
      setMessage(messageElement, resolvedMessage, "error");
    } finally {
      setButtonLoading(uploadButton, false, "Upload");
    }
  });
}

async function createUploadLog() {
  const response = await fetch(`${API_BASE_URL}/upload-log`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      requestedAt: new Date().toISOString(),
    }),
  });

  const data = await readJsonSafely(response);

  if (!response.ok) {
    throw new Error(extractErrorMessage(data, "업로드 로그 생성에 실패했습니다."));
  }

  const uploadId = data.uploadId ?? data.id;

  if (!uploadId) {
    throw new Error("업로드 로그 응답에 uploadId가 없습니다.");
  }

  return uploadId;
}

async function uploadFile(file, uploadId) {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("uploadId", uploadId);

  const response = await fetch(`${API_BASE_URL}/upload`, {
    method: "POST",
    body: formData,
  });

  const data = await readJsonSafely(response);

  if (!response.ok) {
    throw new Error(extractErrorMessage(data, "파일 업로드에 실패했습니다."));
  }

  return data;
}

async function fetchUploadStatus(uploadId) {
  const response = await fetch(`${API_BASE_URL}/upload-status/${encodeURIComponent(uploadId)}`, {
    method: "GET",
  });

  const data = await readJsonSafely(response);

  if (!response.ok) {
    throw new Error(extractErrorMessage(data, "업로드 상태 조회에 실패했습니다."));
  }

  return data;
}

function renderUploadStatus(statusElement, messageElement, uploadId, statusResult) {
  const rawStatus = statusResult.status ?? statusResult.state ?? "unknown";
  const normalizedStatus = String(rawStatus).toLowerCase();
  const detailMessage =
    statusResult.message ??
    statusResult.detail ??
    `최종 상태: ${rawStatus}`;

  if (normalizedStatus.includes("fail") || normalizedStatus.includes("error")) {
    setMessage(statusElement, `업로드 상태 조회 결과: ${rawStatus}`, "error");
    setMessage(messageElement, detailMessage, "error");
    return;
  }

  setMessage(statusElement, `업로드 상태 조회 완료: ${rawStatus} (uploadId: ${uploadId})`, "success");
  setMessage(messageElement, detailMessage, "success");
}

function setMessage(element, text, state) {
  if (!element) {
    return;
  }

  element.textContent = text;
  element.dataset.state = state;
}

function setButtonLoading(button, isLoading, fallbackText) {
  if (!button) {
    return;
  }

  if (!button.dataset.defaultLabel) {
    button.dataset.defaultLabel = button.textContent?.trim() || fallbackText;
  }

  button.disabled = isLoading;
  button.textContent = isLoading ? fallbackText : button.dataset.defaultLabel;
}

function isAllowedFile(fileName) {
  const lowerCaseFileName = fileName.toLowerCase();
  return ALLOWED_EXTENSIONS.some((extension) => lowerCaseFileName.endsWith(extension));
}

async function readJsonSafely(response) {
  try {
    return await response.json();
  } catch (_error) {
    return {};
  }
}

function extractErrorMessage(data, fallbackMessage) {
  if (!data || typeof data !== "object") {
    return fallbackMessage;
  }

  return data.message ?? data.detail ?? fallbackMessage;
}
