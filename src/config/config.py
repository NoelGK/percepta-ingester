import os
from dotenv import load_dotenv
from dataclasses import dataclass
from config.rtsp import RTSPSettings
from config.redis import RedisConfig

load_dotenv()


@dataclass
class Settings:
    REDIS: RedisConfig = RedisConfig()
    MAX_ILL_FRAMES: int = os.getenv("MAX_ILL_FRAMES", 100)
    CAMERA_SHUTDOWN_MAX_TIME: int = os.getenv("CAMERA_SHUTDOWN_MAX_TIME", 20)


settings = Settings()
