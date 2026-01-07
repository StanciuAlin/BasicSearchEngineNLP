from dataclasses import dataclass
from typing import Dict

"""
Module: search_result.py
Description: Defines the data structure used to represent an individual search 
hit. This model encapsulates document metadata, relevance scores, and 
contextual snippets for display in the frontend.
"""


@dataclass
class SearchResult:
    """
    A data transfer object representing a ranked search result.

    This class is used to package the results of the ranking algorithms 
    (BM25, TF-IDF, etc.) into a standardized format. It includes the 
    document's unique identifier, its title, the calculated relevance score, 
    a text snippet for the UI, and metadata regarding term matches.
    """

    doc_id: int
    title: str
    score: float
    snippet: str
    matches: str = ""

    def to_dict(self) -> Dict:
        """
        Serializes the SearchResult instance into a dictionary.

        This method is essential for converting the internal model into a 
        JSON-compatible format required by the FastAPI endpoints and 
        subsequently the .NET Blazor frontend.

        Returns:
            Dict: A dictionary representation of the search result attributes.
        """
        return {
            "doc_id": self.doc_id,
            "title": self.title,
            "score": self.score,
            "snippet": self.snippet,
            "matches": self.matches,
        }
