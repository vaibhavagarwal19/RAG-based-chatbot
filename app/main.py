from fastapi import FastAPI
from pydantic import BaseModel

from app.graph.workflow import app_graph
from app.schemas.state import AgentState

from app.rag.loaders import load_pdf
from app.rag.ingestion import ingest_docs
from app.rag.vector_store import (
    create_vector_store,
    load_vector_store,
    vector_store_exists
)
app = FastAPI()


@app.on_event("startup")
def startup():
    """
    Application startup:
    - Load FAISS from disk if available
    - Otherwise build it from documents
    """
    if vector_store_exists():
        load_vector_store()
        print("✅ FAISS index loaded from disk")
    else:
        docs = load_pdf("data/attention.pdf")
        chunks = ingest_docs(docs)
        create_vector_store(chunks)
        print("✅ FAISS index created and saved")

class QueryRequest(BaseModel):
    query: str


@app.post("/query")
def query_agent(request: QueryRequest):
    """
    Accepts a user query and runs the LangGraph workflow.
    """
    initial_state: AgentState = {
        "user_query": request.query,
        "plan": [],
        "retrieved_docs": [],
        "reasoning": None,
        "validation_status": None,
        "final_answer": None,
        "next_agent": "planner",
    }

    result = app_graph.invoke(initial_state)

    return {
        "answer": result.get("final_answer")
    }
