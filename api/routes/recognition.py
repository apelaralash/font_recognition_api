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
    confidence = recognition_result["confidence"]

    font = await get_font_by_label(db, recognition_result["font"])

    result = RecognitionResult(
        detected_font=font["name"],
        confidence=confidence,
        additional_info=FontInfo(
            font_id="id",
            name=font["name"],
            description=font["description"],
            style=font["style_name"],
            license=font["distribution_method"],
            download_url=font["source"],
            creator_name=font["creator_name"],
        )
    )

    client_ip = "ip10"
    user_agent = "request.headers.get"

    await log_recognition(
        db=db,
        filename=image.filename,
        mimetype=image.content_type,
        font=font["id"],
        confidence=confidence,
        ip_address=client_ip,
        user_agent=user_agent
    )

    return ApiResponse(
        request_id=f"req-{uuid.uuid4().hex[:10]}",
        status="success",
        result=result,
        processed_at=datetime.utcnow().isoformat() + "Z"
    )