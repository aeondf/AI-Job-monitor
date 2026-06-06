from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel
import asyncio

history = []


class SearchRequest(BaseModel):
    text: str


async def fake_parse_jobs(text: str) -> list[dict[str, str]]:
    await asyncio.sleep(1)
    return [
        {"title": "Python Backend", "source": "hh"},
        {"title": "ML Engineer", "source": "linkedin"},
        {"title": "FastAPI Developer", "source": "habr"},
    ]


app = FastAPI()


@app.post("/search")
def search(request: SearchRequest) -> dict[str, str]:
    search_id: str = str(uuid4())
    history.append(
        {
            "search_id": search_id,
            "text": request.text,
        }
    )
    return {"search_id": search_id}


@app.get("/sources")
def get_sources() -> list[str]:
    return ["hh", "linkedin", "habr"]

@app.get("/history")
def show_history() -> list[dict[str, str]]:
    return history


@app.get("/debug/fake-parser")
async def debug_fake_parser() -> list[dict[str, str]]:
    jobs = await fake_parse_jobs("python")
    return jobs