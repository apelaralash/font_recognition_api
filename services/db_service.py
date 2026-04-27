from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from db.models import RecognitionLog, FontLabel, Font, Creator, Style, DistributionMethod

async def log_recognition(
    db: AsyncSession,
    filename: str,
    mimetype: str,
    font: int,
    confidence: float
):
    stmt = insert(RecognitionLog).values(
        filename=filename,
        mimetype=mimetype,
        font_id=font,
        confidence=confidence,
        user_agent=""
    )
    await db.execute(stmt)
    await db.commit()

async def get_font_by_label(db: AsyncSession, label: int) -> dict | None:
    stmt = (
        select(
            Font.id,
            Font.name,
            Font.description,
            Creator.name.label("creator_name"),
            Style.name.label("style_name"),
            DistributionMethod.name.label("distribution_method"),
            Font.source,
            Font.created_at,
            Font.updated_at
        )
        .join(FontLabel, FontLabel.font_id == Font.id)
        .outerjoin(Creator, Font.creator_id == Creator.id)
        .outerjoin(Style, Font.style_id == Style.id)
        .outerjoin(DistributionMethod, Font.distribution_method_id == DistributionMethod.id)
        .where(FontLabel.label == label)
    )

    result = await db.execute(stmt)
    font = result.first()
    if not font:
        return None

    return {
        "id": font.id,
        "name": font.name,
        "description": font.description,
        "creator_name": font.creator_name,
        "style_name": font.style_name,
        "distribution_method": font.distribution_method,
        "source": font.source
    }