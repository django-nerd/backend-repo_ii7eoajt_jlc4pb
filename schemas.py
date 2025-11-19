"""
Database Schemas for TaleQuill

Each Pydantic model represents a collection in MongoDB.
Collection name is the lowercase of the class name.

- Story -> "story"
- Entry -> "entry"
- MemoryEntity -> "memoryentity"

These schemas are used for validation only; MongoDB remains schemaless.
"""
from typing import Optional, Literal, List
from pydantic import BaseModel, Field

class Story(BaseModel):
    """
    A user-owned story object
    """
    title: str = Field(..., description="Story title")
    synopsis: Optional[str] = Field(None, description="Optional one-paragraph premise")
    cover_color: Optional[str] = Field(None, description="Accent color hex (for UI theming)")
    author: Optional[str] = Field(None, description="Display author name")

class Entry(BaseModel):
    """
    A single turn in the story timeline (either user action or AI continuation)
    """
    story_id: str = Field(..., description="ID of the story this entry belongs to")
    role: Literal["user", "ai"] = Field(..., description="Who wrote this entry")
    content: str = Field(..., description="Plain text content of the entry")

class MemoryEntity(BaseModel):
    """
    Tracked memory entity used for retrieval (characters, locations, facts)
    """
    story_id: str = Field(..., description="Story this memory belongs to")
    kind: Literal["character", "location", "fact"] = Field(..., description="Type of memory")
    name: str = Field(..., description="Canonical name of the memory entity")
    description: Optional[str] = Field(None, description="Short description or attributes")
    salience: Optional[int] = Field(3, ge=1, le=5, description="Importance weighting for retrieval")

# Convenience composite used in responses (not a collection)
class StoryWithEntries(BaseModel):
    id: str
    title: str
    synopsis: Optional[str]
    entries: List[dict]
    memory: List[dict]
