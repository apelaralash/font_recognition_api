from pydantic import BaseModel
from typing import Optional, Dict

class FontInfo(BaseModel):
    font_id: str
    name: str
    description: str
    style: Optional[str] = None
    license: Optional[str] = None
    download_url: Optional[str] = None
    creator_name: Optional[str] = None

class RecognitionResult(BaseModel):
    detected_font: str
    confidence: float
    additional_info: Optional[FontInfo] = None

class ApiResponse(BaseModel):
    request_id: str
    status: str
    result: Optional[RecognitionResult] = None
    error: Optional[Dict[str, str]] = None
    processed_at: str