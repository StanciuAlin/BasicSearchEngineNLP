from dataclasses import dataclass

"""
Module: document.py
Description: Defines the primary data model for representing a text document 
within the system. This model serves as the standardized container for 
content during ingestion, indexing, and retrieval.
"""


@dataclass
class Document:
    """
    A data model representing a single document in the corpus.

    This class encapsulates all necessary attributes for a document to be 
    processed by the search engine. It stores the content for snippet 
    generation, the title for display, and a unique identifier for 
    relational mapping within the Inverted Index and Document Store.

    Attributes:
        doc_id (int): A unique numerical identifier assigned to the document.
        title (str): The descriptive name of the document (e.g., filename).
        content (str): The full raw text content of the document.
        path (str): Optional file system path indicating the document's source.
    """
    doc_id: int
    title: str
    content: str
    path: str = ""
