from fastapi import FastAPI
from pydantic import BaseModel
app = FastAPI()

class QueryRequest(BaseModel):
    query: str

@app.get("/")
def read_root():
    return {"Hello": "World"}



@app.post("/query")
def handle_query(request: QueryRequest):
    return {
        "received_query": request.query
    }

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}