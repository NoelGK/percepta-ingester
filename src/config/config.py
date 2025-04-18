import os
from dotenv import load_dotenv
from dataclasses import dataclass
from config.rtsp import RTSPSettings
from config.redis import RedisConfig

load_dotenv()


@dataclass
class Settings:
    RTSP: RTSPSettings = RTSPSettings()
    REDIS: RedisConfig = RedisConfig()

    CONCURRENCY: int = int(os.getenv("CELERY_CONCURRENCY", 1))
    IMAGES_DIR: str = os.getenv("IMAGES_DIR", "/")


settings = Settings()
