from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str

class QuerySource(BaseModel):
    text: str
    score: float
    page_number: int
    filename: str

class QueryResponse(BaseModel):
    answer: str
    sources: list[QuerySource]