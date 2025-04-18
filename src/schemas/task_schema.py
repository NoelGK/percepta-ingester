from pydantic import BaseModel


class TaskSchema(BaseModel):
    name: str
    params: dict
