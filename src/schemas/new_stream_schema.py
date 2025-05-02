from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class NewStreamSchema(BaseModel):
    device_id: str
    host: str
    port: int
    stream: str
    security: Optional[bool] = False
    user: Optional[str] = ''
    password: Optional[str] = ''
    frame_width: Optional[int] = 1920
    frame_height: Optional[int] = 1080

    @property
    def connection_string(self):
        return f"rtsp://{self._credentials()}{self.host}:{self.port}/{self.stream}"
    
    def _credentials(self) -> str:
        if self.security:
            return f"{self.user}:{self.password}@"
        return ''

    @field_validator("device_id")
    def device_id_alphanumeric(cls, field: str):
        if not field.replace('_', '').isalnum():
            raise ValueError("Device id for new camera must contain only alpha-numeric values or '_'")
        return field

    @field_validator("frame_width", "frame_height")
    def frame_size_positive(cls, field: int):
        if field <= 0:
            raise ValueError("Frame dimensions must be positive integers")
        return field
    
    @model_validator(mode="after")
    def security_provided(self):
        if self.security and (not self.user or not self.password):
            raise ValueError("Authentication must be provided if 'security' is enabled")
        return self
