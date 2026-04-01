from fastapi import APIRouter

from app.api.v1.endpoints import cuit

api_router = APIRouter()

api_router.include_router(cuit.router, prefix="/cuit", tags=["cuit"])
