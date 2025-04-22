import redis
from typing import List
from fastapi import FastAPI, APIRouter
from config.config import settings
from config.logging import appLogging as logging
from manager import IngestionManager
from schemas.new_stream_schema import NewStreamSchema

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


@router.post("/new-stream", status_code=200)
def new_stream(new_stream: NewStreamSchema) -> str:
    new_stream_name = manager.add_stream(new_stream)
    return new_stream_name


@router.delete("/stop-stream/{stream_name}", status_code=200)
def stop_stream(stream_name: str) -> bool:
    return manager.remove_stream(stream_name)


@router.get("/active-streams", status_code=200)
def active_streams() -> List:
    return manager.get_active_streams()


api = FastAPI()
logging.info(f"Stream management API initialized")
