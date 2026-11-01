from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import FRONTEND_ORIGIN
from app.routers import chat, documents, fiches, quiz

app = FastAPI(title="Dora", description="Assistant de révision pour étudiants")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(fiches.router)
app.include_router(quiz.router)


@app.get("/health")
def health():
    return {"status": "ok"}
