from fastapi import APIRouter, Request, HTTPException, Depends, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import markdown

from app.models.notes import Note, NoteCreate, NoteUpdate, NoteSummary, create_note_summary
from app.repositories.firestore import get_repository, FirestoreRepository
from app.auth.auth import require_auth, generate_csrf_token

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/notes", response_class=HTMLResponse)
async def notes_list(
    request: Request,
    current_user: str = Depends(require_auth),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """Display notes list page"""
    repository = get_repository()
    offset = (page - 1) * limit
    
    try:
        if search:
            notes = await repository.search_notes(search, limit)
        else:
            notes = await repository.get_notes(limit, offset)
        
        # Create summaries for display
        note_summaries = [create_note_summary(note) for note in notes]
        
        return templates.TemplateResponse("notes_list.html", {
            "request": request,
            "title": "My Notes",
            "notes": note_summaries,
            "search": search,
            "current_page": page,
            "has_next": len(notes) == limit,
            "has_prev": page > 1
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading notes: {str(e)}")


@router.get("/notes/new", response_class=HTMLResponse)
async def create_note_form(
    request: Request,
    current_user: str = Depends(require_auth)
):
    """Display create note form"""
    csrf_token = generate_csrf_token()
    
    return templates.TemplateResponse("note_editor.html", {
        "request": request,
        "title": "Create New Note",
        "note": None,
        "csrf_token": csrf_token,
        "is_editing": False
    })


@router.post("/notes", response_class=HTMLResponse)
async def create_note(
    request: Request,
    current_user: str = Depends(require_auth),
    title: str = Form(...),
    content: str = Form(""),
    csrf_token: str = Form(...)
):
    """Create a new note"""
    # Basic CSRF validation
    if not csrf_token or len(csrf_token) < 32:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
    
    repository = get_repository()
    
    try:
        note_data = NoteCreate(title=title, content=content)
        note = await repository.create_note(note_data)
        
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": "Edit Note",
            "note": note,
            "csrf_token": generate_csrf_token(),
            "is_editing": True,
            "message": "Note created successfully!"
        })
    except ValueError as e:
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": "Create New Note",
            "note": {"title": title, "content": content},
            "csrf_token": generate_csrf_token(),
            "is_editing": False,
            "error": str(e)
        }, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating note: {str(e)}")


@router.get("/notes/{note_id}", response_class=HTMLResponse)
async def get_note_editor(
    request: Request,
    note_id: str,
    current_user: str = Depends(require_auth)
):
    """Display note editor"""
    repository = get_repository()
    
    try:
        note = await repository.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        csrf_token = generate_csrf_token()
        
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": f"Edit: {note.title}",
            "note": note,
            "csrf_token": csrf_token,
            "is_editing": True
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading note: {str(e)}")


@router.post("/notes/{note_id}")
async def update_note(
    request: Request,
    note_id: str,
    current_user: str = Depends(require_auth),
    title: str = Form(...),
    content: str = Form(""),
    csrf_token: str = Form(...)
):
    """Update an existing note"""
    # Basic CSRF validation
    if not csrf_token or len(csrf_token) < 32:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
    
    repository = get_repository()
    
    try:
        note_update = NoteUpdate(title=title, content=content)
        note = await repository.update_note(note_id, note_update)
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": f"Edit: {note.title}",
            "note": note,
            "csrf_token": generate_csrf_token(),
            "is_editing": True,
            "message": "Note updated successfully!"
        })
    except ValueError as e:
        # Return current note data on validation error
        note = await repository.get_note(note_id)
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": f"Edit: {title}",
            "note": {"id": note_id, "title": title, "content": content} if not note else note,
            "csrf_token": generate_csrf_token(),
            "is_editing": True,
            "error": str(e)
        }, status_code=400)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating note: {str(e)}")


@router.delete("/notes/{note_id}")
async def delete_note(
    note_id: str,
    current_user: str = Depends(require_auth)
):
    """Delete a note"""
    repository = get_repository()
    
    try:
        success = await repository.delete_note(note_id)
        if not success:
            raise HTTPException(status_code=404, detail="Note not found")
        
        return {"message": "Note deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting note: {str(e)}")


@router.get("/notes/{note_id}/preview", response_class=HTMLResponse)
async def preview_note(
    request: Request,
    note_id: str,
    current_user: str = Depends(require_auth)
):
    """Display note preview with rendered markdown"""
    repository = get_repository()
    
    try:
        note = await repository.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite'])
        html_content = md.convert(note.content)
        
        return templates.TemplateResponse("note_preview.html", {
            "request": request,
            "title": f"Preview: {note.title}",
            "note": note,
            "html_content": html_content
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing note: {str(e)}")


# API endpoints for AJAX requests
@router.get("/api/notes", response_model=List[NoteSummary])
async def api_get_notes(
    current_user: str = Depends(require_auth),
    search: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """API endpoint to get notes list"""
    repository = get_repository()
    
    try:
        if search:
            notes = await repository.search_notes(search, limit)
        else:
            notes = await repository.get_notes(limit, offset)
        
        return [create_note_summary(note) for note in notes]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading notes: {str(e)}")


@router.get("/api/notes/{note_id}/preview")
async def api_preview_note(
    note_id: str,
    current_user: str = Depends(require_auth)
):
    """API endpoint to get markdown rendered as HTML"""
    repository = get_repository()
    
    try:
        note = await repository.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite'])
        html_content = md.convert(note.content)
        
        return {"html": html_content}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing note: {str(e)}")


@router.post("/api/notes/{note_id}/preview")
async def api_preview_markdown(
    note_id: str,
    request: Request,
    current_user: str = Depends(require_auth)
):
    """API endpoint to preview markdown content without saving"""
    try:
        body = await request.json()
        content = body.get("content", "")
        
        # Convert markdown to HTML
        md = markdown.Markdown(extensions=['extra', 'codehilite'])
        html_content = md.convert(content)
        
        return {"html": html_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing markdown: {str(e)}")