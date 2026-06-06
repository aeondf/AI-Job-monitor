from uuid import uuid4

from fastapi import FastAPI
from pydantic import BaseModel

history = []


class SearchRequest(BaseModel):
    text: str


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
