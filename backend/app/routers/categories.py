"""Categories router — /api/categories endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.database import get_db
from app.schemas.category import CategoryResponse
from app.services import category as category_service

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=list[CategoryResponse])
async def get_categories(
    session: AsyncSession = Depends(get_db),
) -> list[CategoryResponse]:
    """Return all available categories (public endpoint)."""
    categories = await category_service.list_categories(session)
    return [CategoryResponse.model_validate(category) for category in categories]
