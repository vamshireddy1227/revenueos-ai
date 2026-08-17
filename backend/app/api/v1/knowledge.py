from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Document, User
from app.schemas.schemas import DocumentResponse, RagQueryInput, RagQueryOutput
from app.auth.deps import get_current_user
from app.services.rag_engine import rag_engine
from app.services.audit_service import audit_service

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base & RAG"])

class DocumentCreateJSON(BaseModel):
    title: str
    content: str
    file_type: Optional[str] = "txt"

@router.get("/documents", response_model=List[DocumentResponse])
def list_documents(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    docs = db.query(Document).filter(Document.organization_id == current_user.organization_id).order_by(Document.created_at.desc()).all()
    return [DocumentResponse.model_validate(d) for d in docs]

@router.post("/documents", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
def create_document_text(
    req: DocumentCreateJSON,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    raw_text = req.content
    doc = Document(
        organization_id=current_user.organization_id,
        title=req.title,
        file_path=f"{req.title}.{req.file_type}",
        file_type=req.file_type or "txt",
        file_size=len(raw_text.encode("utf-8")),
        is_indexed=False
    )
    db.add(doc)
    db.flush()

    # Index document with RAG engine
    rag_engine.process_and_index_document(db, doc, raw_text)

    audit_service.log(db, current_user.organization_id, "DOCUMENT_INDEXED", "Document", current_user.id, current_user.email, doc.id, {"title": doc.title, "chunks": doc.chunk_count})
    return DocumentResponse.model_validate(doc)

@router.post("/query", response_model=RagQueryOutput)
def query_knowledge_base(
    req: RagQueryInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    res = rag_engine.answer_support_query(db, current_user.organization_id, req.question)
    return RagQueryOutput(
        question=req.question,
        answer=res["answer"],
        confidence=res["confidence"],
        sources=res["sources"],
        escalation_required=res["escalation_required"]
    )

@router.delete("/documents/{doc_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(doc_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id, Document.organization_id == current_user.organization_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "Document not found."}})
    
    db.delete(doc)
    db.commit()
    return None
