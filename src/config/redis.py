import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class RedisConfig:
    host = os.getenv("REDIS_HOST")
    port = os.getenv("REDIS_PORT")
    password = os.getenv("REDIS_PASSWORD")
