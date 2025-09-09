from fastapi import APIRouter, Request, HTTPException, Depends, Query, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
import markdown
import os

from app.models.notes import Note, NoteCreate, NoteUpdate, NoteSummary, create_note_summary
from app.repositories.firestore import get_repository, FirestoreRepository
from app.auth.auth import require_auth, generate_csrf_token
from app.crypto.encryption import encrypt_data, decrypt_data, EncryptionError

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
        
        # Create summaries for display and encrypt sensitive fields
        note_summaries = []
        for note in notes:
            summary = create_note_summary(note)
            # Encrypt title and content_preview for transmission
            try:
                summary_dict = summary.dict()
                summary_dict['title'] = encrypt_data(summary_dict['title'])
                summary_dict['content_preview'] = encrypt_data(summary_dict['content_preview'])
                note_summaries.append(summary_dict)
            except EncryptionError as e:
                raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
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
        # Decrypt incoming encrypted data
        try:
            decrypted_title = decrypt_data(title)
            decrypted_content = decrypt_data(content)
        except EncryptionError as e:
            raise HTTPException(status_code=400, detail=f"Decryption error: {str(e)}")
        
        note_data = NoteCreate(title=decrypted_title, content=decrypted_content)
        note = await repository.create_note(note_data)
        
        # Encrypt note data for template
        try:
            note_dict = note.dict()
            note_dict['title'] = encrypt_data(note_dict['title'])
            note_dict['content'] = encrypt_data(note_dict['content'])
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": "Edit Note",
            "note": note_dict,
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
        
        # Encrypt note data for template
        try:
            note_dict = note.dict()
            note_dict['title'] = encrypt_data(note_dict['title'])
            note_dict['content'] = encrypt_data(note_dict['content'])
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": f"Edit: {note.title}",
            "note": note_dict,
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
        # Decrypt incoming encrypted data
        try:
            decrypted_title = decrypt_data(title)
            decrypted_content = decrypt_data(content)
        except EncryptionError as e:
            raise HTTPException(status_code=400, detail=f"Decryption error: {str(e)}")
        
        note_update = NoteUpdate(title=decrypted_title, content=decrypted_content)
        note = await repository.update_note(note_id, note_update)
        
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        
        # Encrypt note data for template
        try:
            note_dict = note.dict()
            note_dict['title'] = encrypt_data(note_dict['title'])
            note_dict['content'] = encrypt_data(note_dict['content'])
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
        return templates.TemplateResponse("note_editor.html", {
            "request": request,
            "title": f"Edit: {note.title}",
            "note": note_dict,
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
        
        # Encrypt data for template
        try:
            note_dict = note.dict()
            note_dict['title'] = encrypt_data(note_dict['title'])
            note_dict['content'] = encrypt_data(note_dict['content'])
            encrypted_html = encrypt_data(html_content)
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
        return templates.TemplateResponse("note_preview.html", {
            "request": request,
            "title": f"Preview: {note.title}",
            "note": note_dict,
            "html_content": encrypted_html
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
        
        # Encrypt summaries for API response
        encrypted_summaries = []
        for note in notes:
            summary = create_note_summary(note)
            try:
                summary_dict = summary.dict()
                summary_dict['title'] = encrypt_data(summary_dict['title'])
                summary_dict['content_preview'] = encrypt_data(summary_dict['content_preview'])
                encrypted_summaries.append(summary_dict)
            except EncryptionError as e:
                raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        return encrypted_summaries
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
        
        # Convert markdown to HTML and encrypt
        md = markdown.Markdown(extensions=['extra', 'codehilite'])
        html_content = md.convert(note.content)
        
        try:
            encrypted_html = encrypt_data(html_content)
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
        return {"html": encrypted_html}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing note: {str(e)}")


@router.get("/api/notes/{note_id}")
async def api_get_note(
    note_id: str,
    current_user: str = Depends(require_auth)
):
    """API endpoint to get a single note with encrypted fields."""
    repository = get_repository()

    try:
        note = await repository.get_note(note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Prepare response with ISO datetimes and encrypted strings
        note_dict = note.dict()
        if note_dict.get('created_at'):
            note_dict['created_at'] = note_dict['created_at'].isoformat()
        if note_dict.get('updated_at'):
            note_dict['updated_at'] = note_dict['updated_at'].isoformat()

        try:
            note_dict['title'] = encrypt_data(note.title)
            note_dict['content'] = encrypt_data(note.content)
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")

        return note_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error loading note: {str(e)}")

@router.post("/upload")
async def upload_file(
    request: Request,
    current_user: str = Depends(require_auth),
    file: UploadFile = File(...),
    csrf_token: str = Form(...)
):
    """Upload a text file and create a note from its content"""
    print(f"Upload attempt - filename: {file.filename}, content_type: {file.content_type}, csrf_token length: {len(csrf_token) if csrf_token else 0}")
    
    # Basic CSRF validation
    if not csrf_token or len(csrf_token) < 32:
        raise HTTPException(status_code=400, detail="Invalid CSRF token")
    
    # Validate file type
    allowed_extensions = {'.txt', '.md'}
    file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Only .txt and .md files are allowed")
    
    # Check file size (1MB limit)
    MAX_FILE_SIZE = 1024 * 1024  # 1MB in bytes
    
    try:
        # Read file content
        content = await file.read()
        
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File size exceeds 1MB limit")
        
        # Decode content as UTF-8
        try:
            file_content = content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
        
        # Extract filename without extension for title
        filename_base = os.path.splitext(file.filename)[0] if file.filename else "Uploaded File"
        
        # For file uploads, we only encrypt the content, not the filename
        # The filename comes from the original file and is used as-is for the title
        decrypted_title = filename_base
        
        # Decrypt file content (client encrypts before upload)
        try:
            decrypted_content = decrypt_data(file_content)
        except EncryptionError:
            # If decryption fails, assume data is not encrypted (fallback)
            decrypted_content = file_content
        
        # Create note
        repository = get_repository()
        note_data = NoteCreate(title=decrypted_title, content=decrypted_content)
        note = await repository.create_note(note_data)
        
        # Encrypt note data for response
        try:
            # Convert to dict with proper datetime serialization
            note_dict = note.dict()
            # Convert datetimes to ISO format strings
            if note_dict.get('created_at'):
                note_dict['created_at'] = note_dict['created_at'].isoformat()
            if note_dict.get('updated_at'):
                note_dict['updated_at'] = note_dict['updated_at'].isoformat()
            
            note_dict['title'] = encrypt_data(note_dict['title'])
            note_dict['content'] = encrypt_data(note_dict['content'])
        except EncryptionError as e:
            raise HTTPException(status_code=500, detail=f"Encryption error: {str(e)}")
        
        return JSONResponse({
            "success": True,
            "message": "File uploaded successfully",
            "note": note_dict,
            "note_id": note.id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_user: str = Depends(require_auth)
):
    """Display file upload page"""
    csrf_token = generate_csrf_token()
    
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "title": "Upload File",
        "csrf_token": csrf_token
    })


