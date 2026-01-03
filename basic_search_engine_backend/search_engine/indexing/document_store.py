from typing import List
from ..models.document import Document


class DocumentStore:
    def __init__(self, documents: List[Document]):
        self._docs = {d.doc_id: d for d in documents}

    @property
    def documents(self) -> List[Document]:
        return list(self._docs.values())

    def get(self, doc_id: int) -> Document:
        return self._docs[doc_id]
