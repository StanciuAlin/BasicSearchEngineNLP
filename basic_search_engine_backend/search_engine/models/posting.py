from dataclasses import dataclass
from typing import Dict


@dataclass
class Posting:
    doc_id: int
    tf: float  # raw term frequency in that document
