from dataclasses import dataclass


@dataclass
class Document:
    doc_id: int
    title: str
    content: str
