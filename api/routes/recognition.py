from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from datetime import datetime
import uuid

from api.models.response import ApiResponse, RecognitionResult, FontInfo
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import settings
from services.ml_service import recognize_font_by_model
from services.db_service import log_recognition, get_font_by_label
from db.session import get_db

router = APIRouter(prefix="/api/v1/fonts", tags=["Recognition"])

@router.post("/recognize", response_model=ApiResponse)
async def recognition_request(
    image: UploadFile = File(...),
    request: Request = None,
    db: AsyncSession = Depends(get_db)
):
    if image.content_type not in settings.allowed_file_types:
        raise HTTPException(status_code=400, detail="Неподдерживаемый формат изображения")

    contents = await image.read()
    if len(contents) > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Файл слишком большой")
    
    recognition_result = await recognize_font_by_model(contents)
    top_indices = recognition_result["fonts"]
    top_confidences = recognition_result["confidences"]

    results = []

    for rank, (font_idx, confidence) in enumerate(zip(top_indices, top_confidences), start=1):
        # Получаем информацию о шрифте из базы данных
        try:
            # Получаем информацию о шрифте из базы данных
            font = await get_font_by_label(db, font_idx)

            if font:  # проверяем, что шрифт найден
                recognition_result = RecognitionResult(
                    detected_font=font["name"],
                    confidence=float(confidence),
                    rank=rank,
                    additional_info=FontInfo(
                        font_id=f"{font['id']}",
                        name=font["name"],
                        description=font["description"],
                        style=font["style_name"],
                        license=font["distribution_method"],
                        download_url=font["source"],
                        creator_name=font["creator_name"],
                    )
                )
                print(f"asdfg {recognition_result}")
                results.append(recognition_result)
        except Exception as e:
            # Логируем ошибку, но продолжаем обработку остальных шрифтов
            print(f"Ошибка при получении шрифта {font_idx}: {e}")
            continue

    print(f"qwer {results}")

    response = ApiResponse(
        request_id=f"req-{uuid.uuid4().hex[:10]}",
        status="success",
        results=results,
        error=None,
        processed_at=datetime.utcnow().isoformat(),
        total_matches=len(results)
    )
    return response