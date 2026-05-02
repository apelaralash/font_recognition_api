import httpx
import numpy as np
from config.settings import settings
from core.model_loader import load_tf_model
from core.image_processor import preprocess_image_for_model
from fastapi import HTTPException

async def recognize_font_by_model(image_bytes: bytes) -> dict:
    if settings.ml_mode == "local":
        return await recognize_locally(image_bytes)
    elif settings.ml_mode == "remote":
        return await recognize_remotely(image_bytes)
    else:
        raise ValueError("Неверный режим ML_MODE: допустимо 'local' или 'remote'")

async def recognize_locally(image_bytes: bytes, top_k=10) -> dict:
    model = load_tf_model()
    if model is None:
        raise RuntimeError("Модель не загружена")

    try:
        processed = preprocess_image_for_model(image_bytes, target_height=105, target_width=105)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки изображения: {str(e)}")

    # Получаем предсказания модели
    predictions = model.predict(processed, verbose=0)

    # Получаем индексы топ‑K самых вероятных классов (по убыванию уверенности)
    top_indices = np.argsort(predictions[0])[-top_k:][::-1]

    # Получаем соответствующие уверенности
    top_confidences = predictions[0][top_indices]

    return {
        "fonts": top_indices,
        "confidences": top_confidences
    }


async def recognize_remotely(image_bytes: bytes) -> dict:
    url = f"{settings.ml_service_url}/predict"
    files = {"file": ("image.jpg", image_bytes, "image/jpeg")}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, files=files)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=502, detail=f"Ошибка ML-сервиса: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=503, detail=f"Сервис недоступен: {str(e)}")