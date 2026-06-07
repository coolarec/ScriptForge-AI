from fastapi import APIRouter

from app.api.routes import convert, health, sample

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(sample.router)
api_router.include_router(convert.router)
