from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.routers.mock_api import router as mock_api_router


app = FastAPI(title="QA Playwright Portfolio Mock API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mock_api_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
