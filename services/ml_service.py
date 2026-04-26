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

async def recognize_locally(image_bytes: bytes) -> dict:
    model = load_tf_model()
    if model is None:
        raise RuntimeError("Модель не загружена")

    try:
        processed = preprocess_image_for_model(image_bytes, target_height=105, target_width=105)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка обработки изображения: {str(e)}")

    predictions = model.predict(processed, verbose=0)
    confidence = float(np.max(predictions))
    predicted_class = int(np.argmax(predictions))

    classes = [cls.strip() for cls in settings.font_classes.split(",")]
    font_name = classes[predicted_class] if predicted_class < len(classes) else "Unknown"

    return {
        "font": font_name,
        "confidence": confidence
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