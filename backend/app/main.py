from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.materials import router as materials_router
from app.api.articles import router as articles_router
from app.api.agent import router as agent_router
from app.api.profile import router as profile_router

app = FastAPI(title="Read2Post API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"msg": "Read2Post backend ok"}


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "Read2Post"}


app.include_router(materials_router)
app.include_router(articles_router)
app.include_router(agent_router)
app.include_router(profile_router)
