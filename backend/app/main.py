from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.materials import router as materials_router
from app.api.articles import router as articles_router
from app.api.agent import router as agent_router
from app.api.profile import router as profile_router
from app.core.errors import AppError

app = FastAPI(title="NoteForge-AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"msg": "NoteForge-AI backend ok"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "NoteForge-AI"}


@app.exception_handler(AppError)
async def app_error_handler(_, exc: AppError):
    content = {
        "detail": exc.message,
        "code": exc.code,
    }
    if exc.hint:
        content["hint"] = exc.hint
    if exc.detail is not None:
        content["error_detail"] = exc.detail
    return JSONResponse(status_code=exc.status_code, content=content)


app.include_router(materials_router)
app.include_router(articles_router)
app.include_router(agent_router)
app.include_router(profile_router)
