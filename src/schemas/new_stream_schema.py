from typing import Optional
from pydantic import BaseModel


class NewStreamSchema(BaseModel):
    device_id: str
    host: str
    port: str
    stream: str
    security: str
    user: str
    password: str
    frame_width: Optional[int] = 1920
    frame_height: Optional[int] = 1080

    @property
    def connection_string(self):
        return f"rtsp://{self._credentials()}{self.host}:{self.port}/{self.stream}"
    
    def _credentials(self) -> str:
        if self.security != "":
            return f"{self.user}:{self.password}@"
        return ""
