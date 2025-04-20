from dotenv import load_dotenv
from dataclasses import dataclass
from config.rtsp import RTSPSettings
from config.redis import RedisConfig

load_dotenv()


@dataclass
class Settings:
    REDIS: RedisConfig = RedisConfig()


settings = Settings()
