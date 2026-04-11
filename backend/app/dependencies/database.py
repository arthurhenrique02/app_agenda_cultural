from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

import app.database as db_module


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with db_module.AsyncSessionLocal() as session:
        yield session
