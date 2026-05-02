from pydantic import BaseModel
from typing import Optional, List, Dict

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
    rank: int  # ранг в топе (1–10)
    additional_info: Optional[FontInfo] = None

class ApiResponse(BaseModel):
    request_id: str
    status: str
    results: Optional[List[RecognitionResult]] = None  # теперь список
    error: Optional[Dict[str, str]] = None
    processed_at: str
    total_matches: int  # общее количество найденных совпадений
