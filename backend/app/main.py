from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN
from app.routers import chat, documents, fiches, quiz, subjects
from app.services import subjects as subjects_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    subjects_service.migrate_orphan_documents()
    yield


app = FastAPI(title="Dora", description="Assistant de révision pour étudiants", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(subjects.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(fiches.router)
app.include_router(quiz.router)


@app.get("/health")
def health():
    return {"status": "ok"}
