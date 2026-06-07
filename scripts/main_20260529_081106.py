"""Economugin API - Entry point (supports Clean-Architecture evolution)"""

from fastapi import FastAPI
from pydantic import BaseModel

from scripts.api.app_factory import create_app

app: FastAPI = create_app()


# --- Response models for core endpoints ---
class HealthResp(BaseModel):
    status: str
    service: str


class ModelResp(BaseModel):
    count: int
    list: list


# --- Core endpoints (keep here) ---
@app.get("/")
async def root():
    return {"message": "Welcome to Economugin API", "project": "Hydromanugin", "docs": "/docs"}


@app.get("/health", response_model=HealthResp)
async def health():
    return {"status": "ok", "service": "economugin-api"}


@app.get("/models", response_model=ModelResp)
async def list_models():
    return {"count": 5, "list": ["AquaCrop", "RothC", "SWAT+", "HEC-RAS", "LARS-WG"]}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000)
