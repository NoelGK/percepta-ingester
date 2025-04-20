from fastapi import APIRouter
from api.v1.routes import stream_router

api_router = APIRouter()
api_router.include_router(stream_router.router, prefix="", tags=["Base"])
