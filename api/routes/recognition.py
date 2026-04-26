from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from datetime import datetime
import uuid

from api.models.response import ApiResponse, RecognitionResult, FontInfo
from sqlalchemy.ext.asyncio import AsyncSession
from config.settings import settings
from services.ml_service import recognize_font_by_model
from services.db_service import log_recognition
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
    
    font = await recognize_font_by_model(contents)

    result = RecognitionResult(
        detected_font=font["font"],
        confidence=font["confidence"],
        additional_info=FontInfo(
            font_id="times_new_roman",
            name="Times New Roman",
            style="Regular",
            license="Commercial",
            download_url="https://example.com/fonts/times_new",
            sample_image_url="https://example.com",
        )
    )

    client_ip = "ip10"
    user_agent = "request.headers.get"

    await log_recognition(
        db=db,
        filename=image.filename,
        mimetype=image.content_type,
        font=font["font"],
        confidence=font["confidence"],
        ip_address=client_ip,
        user_agent=user_agent
    )

    return ApiResponse(
        request_id=f"req-{uuid.uuid4().hex[:10]}",
        status="success",
        result=result,
        processed_at=datetime.utcnow().isoformat() + "Z"
    )