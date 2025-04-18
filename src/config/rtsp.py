import os
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()


@dataclass
class RTSPSettings:
    HOST: str = os.getenv("CAMERA_HOST")
    PORT: str = os.getenv("CAMERA_PORT")
    STREAM: str = os.getenv("CAMERA_STREAM")
    SECURITY: str = os.getenv("CAMERA_SECURITY")
    USER: str = os.getenv("CAMERA_USER")
    PASSWORD: str = os.getenv("CAMERA_PASSWORD")

    @property
    def connection_string(self):
        return f"rtsp://{self._credentials()}{self.HOST}:{self.PORT}/{self.STREAM}"
    
    def _credentials(self) -> str:
        if self.SECURITY != "":
            return f"{self.USER}:{self.PASSWORD}@"
        return ""
