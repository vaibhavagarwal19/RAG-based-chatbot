import os
import shutil
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.graph.workflow import app_graph
from app.rag.index_builder import get_index_status, initialize_vector_index
from app.rag.ingestion import ingest_docs
from app.rag.loaders import load_pdf
from app.rag.vector_store import add_documents
from app.schemas.state import AgentState


@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("SKIP_INDEX_BUILD") != "1":
        initialize_vector_index()
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/health")
def health():
    """Lightweight health check for Render / load balancers."""
    return {"status": "ok"}


@app.get("/status")
def index_status():
    return get_index_status()


class SourceCitation(BaseModel):
    id: int
    source: str
    page: Optional[int] = None
    excerpt: str


class QueryRequest(BaseModel):
    query: str
    conversation: Optional[List[Dict[str, str]]] = None


class QueryResponse(BaseModel):
    answer: str
    conversation: List[Dict[str, str]] = Field(default_factory=list)
    sources: List[SourceCitation] = Field(default_factory=list)


def _empty_query_response(
    answer: str, conversation: Optional[List[Dict[str, str]]]
) -> QueryResponse:
    return QueryResponse(answer=answer, conversation=conversation or [], sources=[])


@app.post("/query", response_model=QueryResponse)
def query_agent(request: QueryRequest):
    status = get_index_status()
    if status["building"]:
        return _empty_query_response(
            "Still indexing your PDF — first run can take a few minutes. Please wait and try again.",
            request.conversation,
        )
    if status["error"]:
        return _empty_query_response(
            f"Index build failed: {status['error']}",
            request.conversation,
        )
    if not status["ready"]:
        return _empty_query_response(
            "No document index yet. Upload a PDF or add one under the data/ folder, then restart.",
            request.conversation,
        )

    initial_state: AgentState = {
        "user_query": request.query,
        "conversation": request.conversation or [],
        "retrieved_chunks": [],
        "reasoning": None,
        "final_answer": None,
        "sources": [],
    }

    result = app_graph.invoke(initial_state)

    return QueryResponse(
        answer=(result.get("final_answer") or "").strip(),
        conversation=result.get("conversation", []),
        sources=result.get("sources", []),
    )


@app.post("/upload")
def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF files are supported"}

    os.makedirs("data/uploads", exist_ok=True)
    file_path = f"data/uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    status = get_index_status()
    if status["building"]:
        return {"error": "Index is still building. Please wait and try again."}

    docs = load_pdf(file_path)
    chunks = ingest_docs(docs)
    add_documents(chunks)

    return {
        "status": "success",
        "filename": file.filename,
        "chunks_added": len(chunks),
    }
