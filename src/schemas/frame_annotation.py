import ast
import numpy as np
from typing import Any, List, Annotated
from pydantic import BeforeValidator, PlainSerializer


def frame_before_validator(x: Any):
    if isinstance(x, str):
        x = np.array(ast.literal_eval(x), dtype=np.uint8)
    if isinstance(x, List):
        x = np.array(x, dtype=np.uint8)
    return x


def frame_serializer(x: np.ndarray):
    return x.tolist()


AnnotatedFrame = Annotated[
    np.ndarray,
    BeforeValidator(frame_before_validator),
    PlainSerializer(frame_serializer, return_type=List)
]
