from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert
from db.models import RecognitionLog

async def log_recognition(
    db: AsyncSession,
    filename: str,
    mimetype: str,
    font: str,
    confidence: float,
    ip_address: str,
    user_agent: str
):
    stmt = insert(RecognitionLog).values(
        filename=filename,
        mimetype=mimetype,
        font=font,
        confidence=confidence,
        ip_address=ip_address,
        user_agent=user_agent
    )
    await db.execute(stmt)
    await db.commit()