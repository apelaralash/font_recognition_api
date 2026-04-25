from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import AsyncIterator
from fastapi.middleware.cors import CORSMiddleware
from api.routes import recognition
from config.settings import settings
from db.session import engine, get_db
from db import models

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print("🚀 Запуск приложения...")
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)  
    print("✅ Таблицы созданы")

    yield  

    print("🛑 Остановка приложения...")
    engine.dispose()

app = FastAPI(
    title="Font Recognition API",
    description="API для распознавания кириллических шрифтов на изображениях",
    version="0.1.0"
)

app = FastAPI(title="Font Recognition API", lifespan=lifespan)

app.include_router(recognition.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Font Recognition API работает. Документация доступна по /docs"}