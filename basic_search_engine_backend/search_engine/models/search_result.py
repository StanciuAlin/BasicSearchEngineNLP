from dataclasses import dataclass
from typing import Dict


@dataclass
class SearchResult:
    doc_id: int
    title: str
    score: float
    snippet: str
    matches: str = ""

    def to_dict(self) -> Dict:
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "score": self.score,
            "snippet": self.snippet,
            "matches": self.matches,
        }
