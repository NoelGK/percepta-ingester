import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class RTSPSettings:
    device_id: str
    host: str = os.getenv("CAMERA_HOST")
    port: str = os.getenv("CAMERA_PORT")
    stream: str = os.getenv("CAMERA_STREAM")
    security: str = os.getenv("CAMERA_SECURITY")
    user: str = os.getenv("CAMERA_USER")
    password: str = os.getenv("CAMERA_PASSWORD")

    @property
    def connection_string(self):
        return f"rtsp://{self._credentials()}{self.host}:{self.port}/{self.stream}"
    
    def _credentials(self) -> str:
        if self.security != "":
            return f"{self.user}:{self.password}@"
        return ""
