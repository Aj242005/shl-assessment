import logging
from typing import List
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
from app.catalog_store import CatalogStore
from app.assessment import Assessment
from app.config import settings

logger = logging.getLogger(__name__)

class CatalogRetriever:
    def __init__(self, catalog_store: CatalogStore):
        self.catalog = catalog_store
        self.embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.vector_store = self._build_index()

    def _build_index(self) -> FAISS:
        logger.info(f"Building FAISS index with {settings.EMBEDDING_MODEL}...")
        docs = []
        for assessment in self.catalog.get_all():
            text = f"Name: {assessment.name}. "
            if assessment.description:
                text += f"Description: {assessment.description} "
            if assessment.keys:
                text += f"Categories: {', '.join(assessment.keys)}. "
            if assessment.job_levels:
                text += f"Target Job Levels: {', '.join(assessment.job_levels)}. "
            if assessment.duration:
                text += f"Duration: {assessment.duration}. "

            doc = Document(
                page_content=text,
                metadata={"entity_id": assessment.entity_id, "name": assessment.name}
            )
            docs.append(doc)

        vector_store = FAISS.from_documents(docs, self.embeddings)
        logger.info("FAISS index built successfully.")
        return vector_store

    def retrieve(self, query: str, k: int | None = None) -> list[Assessment]:
        if k is None:
            k = settings.RETRIEVAL_K

        docs = self.vector_store.similarity_search(query, k=k)

        results = []
        seen_ids: set[str] = set()

        for doc in docs:
            entity_id = doc.metadata.get("entity_id")
            if entity_id and entity_id not in seen_ids:
                assessment = self.catalog.id_index.get(entity_id)
                if assessment:
                    results.append(assessment)
                    seen_ids.add(entity_id)

        return results
