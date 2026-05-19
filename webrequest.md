# 작업 요청: app/ 영역 테스트용 웹 애플리케이션 구현

현재 프로젝트는 Playwright 기반 QA 자동화 포트폴리오입니다.

이번 작업의 목표는 `app/` 디렉토리에 Playwright가 실제로 조작할 수 있는 간단한 웹 화면을 구현하는 것입니다.

## 작업 범위

`app/` 디렉토리에 아래 파일을 생성해주세요.

```text
app/
├── login.html
├── upload.html
├── app.js
└── style.css
```

## 구현 목표

### 1. 로그인 화면

`login.html`을 구현해주세요.

필수 요소:

- 아이디 입력창
- 비밀번호 입력창
- 로그인 버튼
- 로그인 결과 메시지 영역

Playwright 테스트를 위해 각 요소에는 안정적인 `data-testid`를 부여해주세요.

예시:

```html
<input data-testid="username-input" />
<input data-testid="password-input" />
<button data-testid="login-button">Login</button>
<div data-testid="login-message"></div>
```

## 로그인 동작

로그인 버튼 클릭 시 `app.js`에서 FastAPI Mock 서버의 API를 호출하도록 구현해주세요.

API endpoint:

```text
POST http://localhost:8000/login
```

요청 예시:

```json
{
  "username": "admin",
  "password": "1234"
}
```

성공 시:

- 로그인 성공 메시지 표시
- `upload.html`로 이동

실패 시:

- 로그인 실패 메시지 표시
- 화면 이동하지 않음

---

### 2. 업로드 화면

`upload.html`을 구현해주세요.

필수 요소:

- 파일 선택 input
- 업로드 버튼
- 업로드 상태 메시지 영역
- 업로드 결과 메시지 영역

Playwright 테스트를 위해 각 요소에는 안정적인 `data-testid`를 부여해주세요.

예시:

```html
<input type="file" data-testid="file-input" />
<button data-testid="upload-button">Upload</button>
<div data-testid="upload-status"></div>
<div data-testid="upload-message"></div>
```

## 업로드 동작

업로드 버튼 클릭 시 다음 순서로 API를 호출해주세요.

### 1단계: 업로드 로그 생성

```text
POST http://localhost:8000/upload-log
```

성공 시 서버 응답에서 `uploadId`를 받습니다.

### 2단계: 파일 업로드

```text
POST http://localhost:8000/upload
```

`FormData`를 사용해 파일과 `uploadId`를 함께 전송해주세요.

### 3단계: 업로드 상태 조회

```text
GET http://localhost:8000/upload-status/{uploadId}
```

조회 결과를 화면에 표시해주세요.

---

## 실패 처리 요구사항

다음 상황에 대해 화면에 명확한 메시지를 표시해주세요.

- 파일을 선택하지 않고 업로드 버튼 클릭
- 허용되지 않은 확장자
- 로그인 API 실패
- 업로드 로그 생성 실패
- 파일 업로드 실패
- 상태 조회 실패
- 서버 응답 지연 시 loading 상태 표시

허용 확장자:

```text
.tif, .tiff, .jp2, .jpg, .jpeg, .png, .mp4
```

---

## QA 자동화 관점 요구사항

이 웹은 디자인보다 테스트 가능성이 중요합니다.

다음 조건을 반드시 지켜주세요.

- 모든 주요 요소에 `data-testid` 추가
- JavaScript 함수는 너무 복잡하지 않게 분리
- 에러 메시지는 화면에 표시
- loading 상태 표시
- API 호출 실패 시 사용자에게 원인을 알 수 있는 메시지 표시
- Playwright에서 검증하기 쉬운 DOM 구조 사용
- `alert()` 사용 금지
- console error가 발생하지 않도록 기본 예외 처리 구현

---

## 스타일 요구사항

`style.css`는 간단하고 보기 좋게 작성해주세요.

- 중앙 정렬 레이아웃
- 입력창과 버튼 구분
- 성공 메시지와 실패 메시지 구분
- 너무 화려한 디자인은 불필요

---

## 제약사항

- React, Vue 같은 프레임워크는 사용하지 마세요.
- 순수 HTML, CSS, JavaScript로 구현해주세요.
- 외부 CDN 사용은 최소화해주세요.
- 백엔드 서버는 이미 `localhost:8000`에서 실행된다고 가정해주세요.
- 이번 작업에서는 Playwright 테스트 코드는 작성하지 마세요.
- 이번 작업에서는 FastAPI 서버 코드는 수정하지 마세요.

## 완료 기준

다음 흐름이 브라우저에서 수동으로 동작해야 합니다.

1. `login.html` 접속
2. ID/PW 입력
3. 로그인 버튼 클릭
4. 로그인 성공 시 `upload.html` 이동
5. 파일 선택
6. 업로드 버튼 클릭
7. 업로드 로그 생성
8. 파일 업로드
9. 업로드 상태 조회
10. 화면에 최종 결과 표시

## 추가 요청

작업 완료 후 아래 내용을 함께 정리해주세요.

- 생성한 파일 목록
- 각 파일의 역할
- 수동 테스트 방법
- 이후 Playwright 테스트에서 검증하면 좋은 항목