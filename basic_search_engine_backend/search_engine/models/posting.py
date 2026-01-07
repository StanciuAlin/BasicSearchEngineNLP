from dataclasses import dataclass
from typing import Dict


"""
Module: posting.py
Description: Defines the fundamental unit of the Inverted Index. A Posting 
links a specific term to a document and stores the statistical metadata 
required for relevance ranking.
"""


@dataclass
class Posting:
    """
    Represents an entry in a term's posting list.

    In the context of an Inverted Index, a Posting object stores the 
    relationship between a term and a document. It captures the raw 
    Term Frequency (TF), which is a critical component for calculating 
    weights in both Vector Space Models (TF-IDF) and Probabilistic 
    Models (BM25).

    Attributes:
        doc_id (int): The unique identifier of the document containing the term.
        tf (float): The raw term frequency (count of occurrences) within the document.
    """
    doc_id: int
    tf: float  # raw term frequency in that document
