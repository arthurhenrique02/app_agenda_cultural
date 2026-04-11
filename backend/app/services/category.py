"""Category service — business logic for category listing."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.repositories import category as category_repo


async def list_categories(session: AsyncSession) -> list[Category]:
    """Return categories for public listing."""
    return await category_repo.list_categories(session)
