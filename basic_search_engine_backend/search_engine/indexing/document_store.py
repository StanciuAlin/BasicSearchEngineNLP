import sqlite3
import os
from ..models.document import Document


class DocumentStore:
    def __init__(self, db_path="data/library.db"):
        self.db_path = db_path
        self._setup_db()

    def get_document_count(self) -> int:
        """Returnează numărul total de documente din baza de date."""
        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
            return res[0] if res else 0

    def _setup_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    path TEXT,
                    content TEXT
                )
            """)

    def add_documents(self, documents: list[Document]):
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO documents (id, title, path, content) VALUES (?, ?, ?, ?)",
                [(d.doc_id, d.title, d.path, d.content) for d in documents]
            )

    def get_metadata_list(self):
        """Returnează ID-urile și titlurile fără a încărca textul greu."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT id, title FROM documents").fetchall()

    def get(self, doc_id: int) -> Document:
        """Încarcă un singur document complet din baza de date."""
        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute(
                "SELECT id, title, path, content FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if res:
                return Document(doc_id=res[0], title=res[1], path=res[2], content=res[3])
            raise KeyError(f"Documentul {doc_id} nu a fost găsit.")
