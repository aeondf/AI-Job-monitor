from fastapi import APIRouter

from app.storage import sources

router = APIRouter(tags=["sources"])


@router.get("/sources")
def get_sources() -> list[str]:
    return sources
