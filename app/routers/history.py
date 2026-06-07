from fastapi import APIRouter

from app.storage import history

router = APIRouter(tags=["history"])


@router.get("/history")
def show_history() -> list[dict]:
    return list(history.values())
