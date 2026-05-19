# QA Playwright Portfolio

Playwright 기반의 로그인 및 파일 업로드 UI를 대상으로 E2E 자동화 테스트를 구성한 프로젝트입니다.  
테스트 실행 대상은 간단한 웹 UI와 FastAPI 기반 Mock API 서버입니다.

## 프로젝트 개요

이 프로젝트는 아래 흐름을 자동화 대상으로 다룹니다.

- 로그인
- 파일 업로드
- 업로드 로그 생성
- 업로드 상태 조회
- 예외 및 실패 시나리오 검증
- 네트워크 오류 및 지연 상황 검증

## 기술 스택

| Category | Stack |
|---|---|
| Language | Python |
| UI Automation | Playwright |
| Test Runner | pytest |
| Mock API | FastAPI |
| Web Server | uvicorn |
| Documentation | Markdown |

## 디렉터리 구조

```text
qa-playwright_portfolio/
├─ app/
├─ server/
├─ test-data/
├─ tests/
├─ reports/
├─ .artifacts/
├─ pytest.ini
├─ requirements.txt
└─ readme.md
```

## 디렉터리 설명

### `app/`

테스트 대상 웹 페이지가 들어 있습니다.

- `login.html`: 로그인 화면
- `upload.html`: 파일 업로드 화면
- `app.js`: 로그인, 업로드, 상태 조회 프론트 로직
- `style.css`: 화면 스타일

### `server/`

테스트용 Mock API 서버입니다.

- `main.py`: FastAPI 앱 진입점
- `routers/mock_api.py`: API 라우터
- `services/mock_service.py`: 로그인, 업로드, 상태 조회 동작 및 메모리 상태 관리
- `models/schemas.py`: 요청/응답 스키마

### `tests/`

Playwright 테스트 코드입니다.

- `e2e/`: 실제 시나리오 테스트
- `pages/`: Page Object
- `utils/`: 환경 설정 유틸
- `conftest.py`: 공통 fixture, 브라우저 설정, mock API reset, 실패 증적 수집

### `test-data/`

업로드 검증용 샘플 파일입니다.

- `valid/`: 허용 확장자 샘플
- `invalid/`: 비허용 확장자 샘플

### `reports/`

리포트용 예약 디렉터리입니다. 현재 기본 실행 결과는 이 폴더에 직접 저장하지 않습니다.

### `.artifacts/`

테스트 실패 시 자동 생성되는 디버깅 산출물 저장 위치입니다.

- `screenshots/`: 실패 시점 전체 화면 캡처
- `traces/`: Playwright trace zip
- `logs/`: 브라우저 console, request failure, HTTP error 로그
- `videos/`: 실패 테스트 동영상

## 현재 구현 범위

### 로그인

- 정상 로그인 후 업로드 페이지 이동
- 잘못된 비밀번호 처리
- 빈 폼 제출 처리
- 세션 만료 응답 처리
- 서버 오류 응답 처리
- 로그인 API 네트워크 오류 처리

### 파일 업로드

- 정상 업로드
- 허용되지 않은 확장자 차단
- 중복 파일명 업로드 차단
- 파일 미선택 제출 처리
- 업로드 처리 실패 상태 처리
- 업로드 상태 조회 API 오류 처리
- 업로드 로그 생성 네트워크 오류 처리
- 느린 상태 조회 중 loading 상태 확인

### 샘플 파일 기반 업로드

`test-data/valid`와 `test-data/invalid`의 실제 파일을 자동 탐지해 테스트를 생성합니다.

- `test-data/valid/`: 성공해야 하는 샘플 파일
- `test-data/invalid/`: 실패해야 하는 샘플 파일
- `.gitkeep`를 제외한 파일은 자동으로 테스트 대상에 포함됩니다.
- 허용 확장자: `jpg`, `jpeg`, `png`, `tif`, `tiff`, `jp2`, `mp4`
- 그 외 확장자는 `invalid/`에 두는 것을 기준으로 사용합니다.
- `valid/`에 비허용 확장자를 넣거나 `invalid/`에 허용 확장자를 넣으면, 테스트가 분류 오류를 명확한 메시지로 알려줍니다.

## 테스트 현황

자동화 테스트 수는 `test-data` 내 샘플 파일 개수에 따라 달라질 수 있습니다.

- 로그인 시나리오
- 업로드 시나리오
- 샘플 파일 반복 업로드 시나리오

전체 실행:

```bash
pytest -q
```

## Mock API 엔드포인트

| Method | Endpoint | Description |
|---|---|---|
| POST | `/login` | 로그인 |
| POST | `/upload-log` | 업로드 로그 생성 |
| POST | `/upload` | 파일 업로드 |
| GET | `/upload-status/{id}` | 업로드 상태 조회 |
| POST | `/test/reset` | 테스트용 서버 상태 초기화 |

## 설치 방법

### 1. 가상환경 생성

```bash
python -m venv .venv
```

### 2. 가상환경 활성화

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

### 4. Playwright 브라우저 설치

```bash
python -m playwright install
```

## 실행 방법

### 1. Mock API 서버 실행

```bash
uvicorn server.main:app --reload
```

기본 주소:

- API: `http://localhost:8000`

### 2. 웹 페이지 실행

정적 HTML을 열 수 있는 로컬 서버를 실행해야 합니다. 예시는 아래와 같습니다.

```bash
python -m http.server 5500 --directory app
```

기본 주소:

- APP: `http://localhost:5500`

### 3. 테스트 실행

전체 실행:

```bash
pytest
```

조용한 출력:

```bash
pytest -q
```

특정 파일만 실행:

```bash
pytest tests/e2e/test_login.py
pytest tests/e2e/test_upload.py
pytest tests/e2e/test_upload_files.py
```

특정 테스트만 실행:

```bash
pytest tests/e2e/test_upload.py::test_upload_rejects_duplicate_filename
```

수집된 테스트 목록만 확인:

```bash
pytest --collect-only -q
```

## 일반 테스터용 사용 가이드

코드 수정 없이 테스트만 실행하려는 경우 아래 순서대로 진행하면 됩니다.

### 사전 준비

1. Python 설치
2. 프로젝트 폴더 열기
3. 가상환경 생성 및 활성화
4. `pip install -r requirements.txt`
5. `python -m playwright install`

### 실행 순서

터미널 1:

```bash
uvicorn server.main:app --reload
```

터미널 2:

```bash
python -m http.server 5500 --directory app
```

터미널 3:

```bash
pytest -q
```

### 테스트 결과 확인

- 모든 테스트 통과 시: `24 passed` 형태로 표시
- 실패 시: pytest 출력에서 실패 테스트 이름 확인
- 추가 증적 확인:
  - `.artifacts/screenshots`
  - `.artifacts/traces`
  - `.artifacts/logs`
  - `.artifacts/videos`

### 자주 사용하는 실행 예시

로그인 테스트만 실행:

```bash
pytest tests/e2e/test_login.py -q
```

업로드 테스트만 실행:

```bash
pytest tests/e2e/test_upload.py -q
```

샘플 파일 업로드 테스트만 실행:

```bash
pytest tests/e2e/test_upload_files.py -q
```

샘플 파일 분류 규칙 확인:

- `valid/`는 업로드 성공을 기대하는 파일만 둡니다.
- `invalid/`는 업로드 실패를 기대하는 파일만 둡니다.
- 예: `sample.tiff.exe`는 마지막 확장자가 `.exe`이므로 `invalid/`에 두어야 합니다.

## 테스트 설계 원칙

- `data-testid` 기반 locator 우선 사용
- Playwright auto-wait 적극 활용
- 고정 sleep 최소화
- page object로 UI 조작 분리
- 네트워크 오류와 실패 응답도 명시적으로 검증
- 테스트 간 서버 상태 오염 방지를 위해 매 테스트 시작 전 mock API 상태 초기화

## 환경 변수

기본값은 아래와 같으며, 필요 시 환경 변수로 변경할 수 있습니다.

- `APP_BASE_URL`: 기본값 `http://localhost:5500`
- `API_BASE_URL`: 기본값 `http://localhost:8000`

## 디버깅 자료

테스트 실패 시 아래 자료가 자동 생성됩니다.

- screenshot
- trace
- video
- browser log

이 자료는 `.artifacts/` 아래에 저장되며, 성공한 테스트는 기본적으로 산출물을 남기지 않습니다.

## 참고 사항

- 현재 UI 및 API 메시지 문자열에는 인코딩 이슈가 일부 남아 있을 수 있습니다.
- 신규 테스트 코드는 가능한 한 문구 전문 비교보다 `data-state`, URL, 상태값, `data-testid` 기준 검증을 우선합니다.
- `reports/`는 향후 리포트 연동을 위한 예약 디렉터리로 유지합니다.

## License

MIT License
