import sqlite3
import os
from ..models.document import Document

"""
Module: document_store.py
Description: Implements a persistent storage layer for documents using SQLite. 
This module ensures that the indexed corpus is saved on disk, allowing for 
incremental updates and efficient metadata retrieval without loading full text into memory.
"""


class DocumentStore:
    """
    A persistent repository for managing document data.

    The DocumentStore acts as a Bridge between the local file system and the 
    Inverted Index. By utilizing an embedded SQLite database, it provides 
    efficient CRUD operations and allows the search engine to retrieve 
    document titles and snippets quickly during query execution.
    """

    def __init__(self, db_path="data/library.db"):
        """
        Initializes the document store and prepares the underlying database.

        Args:
            db_path (str): The file path to the SQLite database.
        """

        self.db_path = db_path
        self._setup_db()

    def get_document_count(self) -> int:
        """
        Retrieves the total volume of documents currently stored in the repository.

        Returns:
            int: Total number of records in the 'documents' table.
        """

        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute("SELECT COUNT(*) FROM documents").fetchone()
            return res[0] if res else 0

    def _setup_db(self):
        """
        Initializes the database schema if it is not already present.

        Ensures the existence of the directory structure and creates the 
        'documents' table with primary keys and text fields for content and metadata.
        """

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
        """
        Performs a bulk insertion or update of documents in the database.

        This method uses an 'INSERT OR REPLACE' strategy to ensure that 
        documents with existing IDs are updated with new content, preventing 
        duplicates while allowing for corpus synchronization.

        Args:
            documents (list[Document]): A list of Document model instances to be persisted.
        """

        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR REPLACE INTO documents (id, title, path, content) VALUES (?, ?, ?, ?)",
                [(d.doc_id, d.title, d.path, d.content) for d in documents]
            )

    def get_metadata_list(self):
        """
        Retrieves high-level metadata for all indexed documents.

        This method is optimized for UI listing and selection, as it only 
        fetches IDs and titles, avoiding the memory overhead of loading 
        large text blocks.

        Returns:
            list: A list of tuples containing (id, title).
        """

        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT id, title FROM documents").fetchall()

    def get(self, doc_id: int) -> Document:
        """
        Retrieves a complete Document object by its unique identifier.

        Args:
            doc_id (int): The unique ID of the document to load.

        Returns:
            Document: An instance of the Document model populated with database data.

        Raises:
            KeyError: If the requested document ID does not exist in the store.
        """

        with sqlite3.connect(self.db_path) as conn:
            res = conn.execute(
                "SELECT id, title, path, content FROM documents WHERE id = ?", (doc_id,)).fetchone()
            if res:
                return Document(doc_id=res[0], title=res[1], path=res[2], content=res[3])
            raise KeyError(
                f"The document {doc_id} was not found in the database.")
