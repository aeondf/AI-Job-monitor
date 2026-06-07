from fastapi import APIRouter

from app.services.parsers import (
    fetch_real_vacancies,
    fetch_remoteok_vacancies,
    fetch_remotive_vacancies,
)
from app.services.rag import rank_vacancies

router = APIRouter(prefix="/debug", tags=["debug"])


@router.get("/remotive")
async def debug_remotive() -> list[dict]:
    return await fetch_remotive_vacancies("python", limit=5)


@router.get("/remoteok")
async def debug_remoteok() -> list[dict]:
    return await fetch_remoteok_vacancies(limit=5)


@router.get("/rag")
async def debug_rag() -> list[dict]:
    vacancies = await fetch_real_vacancies("python backend", limit=20)
    return rank_vacancies(
        vacancies,
        query="python backend",
        profile="FastAPI async Python Docker PostgreSQL",
        limit=5,
    )
