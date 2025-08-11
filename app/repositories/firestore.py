from datetime import datetime
from typing import List, Optional
import logging
from google.cloud import firestore
from google.cloud.firestore_v1.base_query import FieldFilter

from app.models.notes import Note, NoteCreate, NoteUpdate
from app.config import settings

logger = logging.getLogger(__name__)


class FirestoreRepository:
    """Firestore repository for notes management"""
    
    def __init__(self):
        try:
            if settings.firestore_project:
                self.db = firestore.Client(project=settings.firestore_project)
            else:
                # Use default project from environment
                self.db = firestore.Client()
            self.collection_name = "notes"
        except Exception as e:
            logger.error(f"Failed to initialize Firestore client: {e}")
            raise
    
    def _doc_to_note(self, doc) -> Note:
        """Convert Firestore document to Note model"""
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        return Note(
            id=doc.id,
            title=data.get("title", ""),
            content=data.get("content", ""),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )
    
    async def create_note(self, note_data: NoteCreate) -> Note:
        """Create a new note in Firestore"""
        try:
            now = datetime.utcnow()
            doc_data = {
                "title": note_data.title,
                "content": note_data.content,
                "created_at": now,
                "updated_at": now
            }
            
            # Add document and get reference
            doc_ref = self.db.collection(self.collection_name).add(doc_data)[1]
            
            # Return the created note
            return Note(
                id=doc_ref.id,
                title=note_data.title,
                content=note_data.content,
                created_at=now,
                updated_at=now
            )
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            raise
    
    async def get_note(self, note_id: str) -> Optional[Note]:
        """Get a single note by ID"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(note_id)
            doc = doc_ref.get()
            return self._doc_to_note(doc)
        except Exception as e:
            logger.error(f"Error getting note {note_id}: {e}")
            raise
    
    async def get_notes(self, limit: int = 50, offset: int = 0) -> List[Note]:
        """Get paginated list of notes, ordered by updated_at desc"""
        try:
            query = (self.db.collection(self.collection_name)
                    .order_by("updated_at", direction=firestore.Query.DESCENDING)
                    .limit(limit)
                    .offset(offset))
            
            docs = query.stream()
            notes = []
            for doc in docs:
                note = self._doc_to_note(doc)
                if note:
                    notes.append(note)
            
            return notes
        except Exception as e:
            logger.error(f"Error getting notes: {e}")
            raise
    
    async def update_note(self, note_id: str, note_update: NoteUpdate) -> Optional[Note]:
        """Update an existing note"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(note_id)
            
            # Check if note exists
            if not doc_ref.get().exists:
                return None
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow()
            }
            
            if note_update.title is not None:
                update_data["title"] = note_update.title
            
            if note_update.content is not None:
                update_data["content"] = note_update.content
            
            # Update document
            doc_ref.update(update_data)
            
            # Return updated note
            updated_doc = doc_ref.get()
            return self._doc_to_note(updated_doc)
            
        except Exception as e:
            logger.error(f"Error updating note {note_id}: {e}")
            raise
    
    async def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID"""
        try:
            doc_ref = self.db.collection(self.collection_name).document(note_id)
            
            # Check if note exists before deletion
            if not doc_ref.get().exists:
                return False
            
            doc_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Error deleting note {note_id}: {e}")
            raise
    
    async def search_notes(self, query: str, limit: int = 50) -> List[Note]:
        """Search notes by title and content"""
        try:
            notes = []
            
            # Firestore doesn't support full-text search natively
            # We'll implement a simple search by fetching all notes and filtering
            # In production, you might want to use Firestore's array-contains
            # or implement external search with Elasticsearch/Algolia
            
            all_docs = (self.db.collection(self.collection_name)
                       .order_by("updated_at", direction=firestore.Query.DESCENDING)
                       .limit(1000)  # Reasonable limit for search
                       .stream())
            
            query_lower = query.lower()
            
            for doc in all_docs:
                note = self._doc_to_note(doc)
                if note and (
                    query_lower in note.title.lower() or 
                    query_lower in note.content.lower()
                ):
                    notes.append(note)
                    if len(notes) >= limit:
                        break
            
            return notes
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            raise
    
    async def get_notes_count(self) -> int:
        """Get total count of notes"""
        try:
            # Firestore doesn't have a direct count method
            # For large datasets, you'd maintain a counter document
            docs = list(self.db.collection(self.collection_name).stream())
            return len(docs)
        except Exception as e:
            logger.error(f"Error counting notes: {e}")
            raise


# Global repository instance
_repository = None

def get_repository() -> FirestoreRepository:
    """Get or create repository instance"""
    global _repository
    if _repository is None:
        _repository = FirestoreRepository()
    return _repository