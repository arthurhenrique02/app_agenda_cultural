from fastapi import FastAPI

from app.routers import auth as auth_router
from app.routers import categories as categories_router
from app.routers import events as events_router
from app.routers import users as users_router

app = FastAPI(
    title="Agenda Cultural API",
    description="Cultural events platform API",
    version="0.1.0",
)

app.include_router(auth_router.router)
app.include_router(categories_router.router)
app.include_router(events_router.router)
app.include_router(users_router.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
