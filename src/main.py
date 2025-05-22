import redis
from typing import List
from fastapi import FastAPI, APIRouter
from config.config import settings
from config.logging import appLogging as logging
from manager import IngestionManager
from schemas.stream_schema import StreamSchema

logging.info(f"Starting ingestion pipeline...")

# Ingestion manager
redis_client = redis.Redis(
    host=settings.REDIS.host,
    port=settings.REDIS.port,
    password=settings.REDIS.password
)
logging.info(f"Connected to Redis at {settings.REDIS.host}")

manager = IngestionManager(redis_client)
logging.info(f"Ingestion manager initialized")

# API router and endpoints
router = APIRouter(prefix="/api/v1", tags=["Base"])


@router.post("/start-stream", status_code=200)
def start_stream(stream: StreamSchema) -> str:
    new_stream_name = manager.start_stream(stream)
    return new_stream_name


@router.delete("/stop-stream/{stream_id}", status_code=200)
def stop_stream(stream_id: int) -> bool:
    return manager.stop_stream(stream_id)


@router.get("/active-streams", status_code=200)
def active_streams() -> List:
    return manager.get_active_streams()


api = FastAPI(
    title="Percepta Ingestion manager API",
    description="API for managing video stream ingestion using FFmpeg and Redis Streams.",
    version="1.0.0",
    docs_url="/docs",           # Swagger UI
    redoc_url="/redoc",         # ReDoc alternative
    openapi_url="/openapi.json" # OpenAPI schema
)
api.include_router(router)
logging.info(f"Stream management API initialized")
