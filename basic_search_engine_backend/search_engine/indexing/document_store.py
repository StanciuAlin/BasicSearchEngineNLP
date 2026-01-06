import sqlite3
import os
from ..models.document import Document


class DocumentStore:
    """A simple document store using SQLite for persistence."""

    def __init__(self, db_path="data/library.db"):
        self.db_path = db_path
        self._setup_db()

    def get_document_count(self) -> int:
        """Returns the total number of documents in the database."""

        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
            return res[0] if res else 0

    def _setup_db(self):
        """Creates the documents table if it doesn't exist."""

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
        """Adds a list of documents to the database."""

        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO documents (id, title, path, content) VALUES (?, ?, ?, ?)",
                [(d.doc_id, d.title, d.path, d.content) for d in documents]
            )

    def get_metadata_list(self):
        """Returns document IDs and titles without loading the heavy text."""

        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT id, title FROM documents").fetchall()

    def get(self, doc_id: int) -> Document:
        """Loads a single document from the database."""

        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute(
                "SELECT id, title, path, content FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if res:
                return Document(doc_id=res[0], title=res[1], path=res[2], content=res[3])
            raise KeyError(
                f"The document {doc_id} was not found in the database.")
