import math
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Document, DocumentChunk
from app.services.ai_provider import ai_provider

class RAGEngineService:
    """
    RAG (Retrieval-Augmented Generation) Engine.
    Handles document parsing, text chunking, embedding index generation,
    vector cosine similarity calculation, and RAG grounded query generation.
    """

    @staticmethod
    def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Split document text into overlapping token/character chunks."""
        words = text.split()
        if not words:
            return []
        
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
            if i >= len(words):
                break
        return chunks

    @staticmethod
    def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Compute cosine similarity between two float embedding vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = math.sqrt(sum(a * a for a in vec_a))
        norm_b = math.sqrt(sum(b * b for b in vec_b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)

    def process_and_index_document(self, db: Session, document: Document, raw_content: str):
        """Chunk text, generate embeddings, and save indexed chunks in DB."""
        # Delete old chunks if re-indexing
        db.query(DocumentChunk).filter(DocumentChunk.document_id == document.id).delete()
        
        chunks_text = self.chunk_text(raw_content)
        for idx, chunk_str in enumerate(chunks_text):
            embedding = ai_provider.get_embedding(chunk_str)
            chunk_obj = DocumentChunk(
                document_id=document.id,
                organization_id=document.organization_id,
                chunk_index=idx,
                content=chunk_str,
                embedding_json=embedding,
                metadata_json={"doc_title": document.title, "chunk_index": idx}
            )
            db.add(chunk_obj)
        
        document.chunk_count = len(chunks_text)
        document.is_indexed = True
        db.commit()

    def search_similar_chunks(
        self,
        db: Session,
        organization_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        """Retrieve top_k most relevant document chunks for the organization using vector similarity."""
        query_embedding = ai_provider.get_embedding(query)
        
        # Load all tenant-scoped chunks
        chunks = db.query(DocumentChunk).filter(
            DocumentChunk.organization_id == organization_id
        ).all()

        scored_chunks = []
        for chunk in chunks:
            if chunk.embedding_json:
                sim = self.cosine_similarity(query_embedding, chunk.embedding_json)
                scored_chunks.append({
                    "id": chunk.id,
                    "document_id": chunk.document_id,
                    "content": chunk.content,
                    "similarity": sim,
                    "doc_title": chunk.metadata_json.get("doc_title", "Doc") if chunk.metadata_json else "Doc"
                })

        # Sort by highest similarity
        scored_chunks.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_chunks[:top_k]

    def answer_support_query(
        self,
        db: Session,
        organization_id: str,
        question: str
    ) -> Dict[str, Any]:
        """Perform RAG search and generate grounded answer."""
        top_chunks = self.search_similar_chunks(db, organization_id, question, top_k=3)
        return ai_provider.answer_rag_question(question, top_chunks)

rag_engine = RAGEngineService()
