from fastapi import FastAPI

from app.routers import auth as auth_router

app = FastAPI(
    title="Agenda Cultural API",
    description="Cultural events platform API",
    version="0.1.0",
)

app.include_router(auth_router.router)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
