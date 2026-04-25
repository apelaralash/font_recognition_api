from pydantic import BaseModel
from typing import Optional

class RecognizeRequest(BaseModel):
    user_id: Optional[str] = None