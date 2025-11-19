from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Story, Entry, MemoryEntity

app = FastAPI(title="TaleQuill API", version="0.1.0")

# CORS for local dev + hosted preview
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Utilities

def to_object_id(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID")

# Health + schema endpoints

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/test")
def test_db():
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    return {"status": "ok", "db": True}

# Stories

@app.post("/stories", response_model=dict)
def create_story(story: Story):
    story_id = create_document("story", story)
    return {"id": story_id}

@app.get("/stories", response_model=List[dict])
def list_stories():
    items = get_documents("story")
    # shape minimal metadata
    return [
        {
            "id": str(it.get("_id")),
            "title": it.get("title"),
            "synopsis": it.get("synopsis"),
            "cover_color": it.get("cover_color"),
            "author": it.get("author"),
            "created_at": it.get("created_at"),
        }
        for it in items
    ]

# Entries

@app.post("/stories/{story_id}/entries", response_model=dict)
def add_entry(story_id: str, entry: Entry):
    # ensure path/body match
    if entry.story_id != story_id:
        raise HTTPException(status_code=400, detail="story_id mismatch")
    _ = to_object_id(story_id)  # validate
    entry_id = create_document("entry", entry)
    return {"id": entry_id}

@app.get("/stories/{story_id}/entries", response_model=List[dict])
def get_entries(story_id: str):
    _ = to_object_id(story_id)
    docs = get_documents("entry", {"story_id": story_id})
    return [
        {
            "id": str(d.get("_id")),
            "role": d.get("role"),
            "content": d.get("content"),
            "created_at": d.get("created_at"),
        }
        for d in docs
    ]

# Memory

@app.post("/stories/{story_id}/memory", response_model=dict)
def add_memory(story_id: str, memory: MemoryEntity):
    if memory.story_id != story_id:
        raise HTTPException(status_code=400, detail="story_id mismatch")
    _ = to_object_id(story_id)
    mem_id = create_document("memoryentity", memory)
    return {"id": mem_id}

@app.get("/stories/{story_id}/memory", response_model=List[dict])
def get_memory(story_id: str):
    _ = to_object_id(story_id)
    docs = get_documents("memoryentity", {"story_id": story_id})
    return [
        {
            "id": str(d.get("_id")),
            "kind": d.get("kind"),
            "name": d.get("name"),
            "description": d.get("description"),
            "salience": d.get("salience"),
        }
        for d in docs
    ]

# Simple generate endpoint (stub for now - no external LLM calls)
class GenerateRequest(BaseModel):
    story_id: str
    prompt: str

@app.post("/generate", response_model=dict)
def generate_next(req: GenerateRequest):
    # Placeholder deterministic continuation to keep demo self-contained.
    # In production, plug into your LLM with RAG using the memory.
    _ = to_object_id(req.story_id)
    continuation = (
        "The narrative continues with measured cadence, drawing threads together. "
        "Embodied motifs resurface; choices cast earlier begin to matter."
    )
    entry = Entry(story_id=req.story_id, role="ai", content=continuation)
    entry_id = create_document("entry", entry)
    return {"id": entry_id, "content": continuation}
