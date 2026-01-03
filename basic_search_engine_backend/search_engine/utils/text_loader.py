import os
from typing import List
from ..models.document import Document


def load_documents_from_folder(folder: str) -> List[Document]:
    docs: List[Document] = []
    doc_id = 0
    for fname in sorted(os.listdir(folder)):
        if not fname.lower().endswith(".txt"):
            continue
        path = os.path.join(folder, fname)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        title = os.path.splitext(fname)[0]
        docs.append(Document(doc_id=doc_id, title=title, content=content))
        doc_id += 1
    return docs
