from pydantic import BaseModel


class SearchRequest(BaseModel):
    text: str
    profile: str = ""
    limit: int = 10


class SearchResponse(BaseModel):
    search_id: str
