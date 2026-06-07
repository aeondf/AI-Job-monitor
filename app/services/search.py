from uuid import uuid4

from app.services.parsers import fetch_real_vacancies
from app.services.rag import rank_vacancies
from app.storage import history


def create_search(text: str, profile: str = "", limit: int = 10) -> str:
    search_id = str(uuid4())

    history[search_id] = {
        "search_id": search_id,
        "text": text,
        "profile": profile,
        "limit": limit,
        "status": "running",
        "jobs": [],
        "message": "Fetching real vacancies",
    }

    return search_id


async def run_search(
    search_id: str,
    text: str,
    profile: str = "",
    limit: int = 10,
) -> None:
    try:
        vacancies = await fetch_real_vacancies(text, limit=max(limit * 3, 20))
        jobs = rank_vacancies(vacancies, query=text, profile=profile, limit=limit)
    except Exception as error:
        if search_id in history:
            history[search_id]["status"] = "failed"
            history[search_id]["message"] = str(error)
        return

    if search_id not in history:
        return

    history[search_id]["status"] = "finished"
    history[search_id]["jobs"] = jobs
    history[search_id]["message"] = f"Found {len(jobs)} relevant vacancies"

    print(f"Search {search_id} finished: {len(jobs)} ranked jobs")
