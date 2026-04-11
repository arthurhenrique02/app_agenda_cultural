from fastapi import FastAPI

app = FastAPI(
    title="Agenda Cultural API",
    description="Cultural events platform API",
    version="0.1.0",
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}
