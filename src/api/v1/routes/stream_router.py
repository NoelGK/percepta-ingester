from fastapi import APIRouter

router = APIRouter()


@router.post("/add-stream", status_code=200)
def add_stream():
    pass
