"""Category repository — direct DB access for categories."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category


async def list_categories(session: AsyncSession) -> list[Category]:
    """Return all categories ordered by name."""
    result = await session.execute(select(Category).order_by(Category.name.asc()))
    return list(result.scalars().all())
