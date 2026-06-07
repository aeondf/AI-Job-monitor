import asyncio

from fastapi import APIRouter

from app.schemas import SearchRequest, SearchResponse
from app.services.search import create_search, run_search

router = APIRouter(tags=["search"])


@router.post("/search")
async def start_search(request: SearchRequest) -> SearchResponse:
    search_id = create_search(request.text, request.profile, request.limit)
    asyncio.create_task(
        run_search(search_id, request.text, request.profile, request.limit)
    )

    return SearchResponse(search_id=search_id)
