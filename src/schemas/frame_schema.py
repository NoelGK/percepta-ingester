from pydantic import BaseModel, ConfigDict
from datetime import datetime
from schemas.frame_annotation import AnnotatedFrame


class FrameSchema(BaseModel):
    datetime: datetime
    data: AnnotatedFrame

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
