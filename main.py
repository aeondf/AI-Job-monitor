from fastapi import FastAPI
from pydantic import BaseModel


class SearchesRequest(BaseModel):
    text: str


app = FastAPI()


@app.post("/search")
def search(request: SearchesRequest) -> dict[str, str]:
    return {"search_id": "123"}


@app.get("/sources")
def get_sources() -> list[str]:
    return ["headhunter", "LinkedIn", "HubrCareer"]
