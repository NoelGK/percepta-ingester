from fastapi import APIRouter
from config.config import settings
from ffmpeg import FFmpegWatcher
from config.logging import appLogging as logging
from schemas.new_stream_schema import NewStreamSchema

# Ingestion 
manager = IngestionManager()


# API router and endpoints
router = APIRouter(prefix="/api/v1", tags=["Base"])


@router.post("/new-stream", status_code=200)
def new_stream(new_stream: NewStreamSchema):
    pass
