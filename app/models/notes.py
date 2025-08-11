from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator


class Note(BaseModel):
    """Note data model as specified in PRD"""
    id: Optional[str] = None
    title: str = Field(..., max_length=255, description="Note title (max 255 chars)")
    content: str = Field(..., description="Note content in markdown format")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        # Content can be empty, but if provided should be a string
        return v if v is not None else ""
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class NoteCreate(BaseModel):
    """Model for creating a new note"""
    title: str = Field(..., max_length=255)
    content: str = ""
    
    @validator('title')
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()


class NoteUpdate(BaseModel):
    """Model for updating an existing note"""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    
    @validator('title')
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Title cannot be empty')
        return v.strip() if v else None


class NoteResponse(BaseModel):
    """Model for note responses"""
    id: str
    title: str
    content: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class NoteSummary(BaseModel):
    """Model for note list/summary responses"""
    id: str
    title: str
    content_preview: str = Field(..., description="First 200 chars of content")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


def create_note_summary(note: Note) -> NoteSummary:
    """Create a summary from a full note"""
    preview = note.content[:200] + "..." if len(note.content) > 200 else note.content
    return NoteSummary(
        id=note.id,
        title=note.title,
        content_preview=preview,
        created_at=note.created_at,
        updated_at=note.updated_at
    )