# basic_search_engine_backend/search_engine/preprocessing/tokenizer.py
# A simple tokenizer implementation for text preprocessing in a search engine.
# First step towards building a more complex NLP pipeline.
import re
from typing import List

# Educational simple regex-based tokenizer.
TOKEN_PATTERN = re.compile(r"[A-Za-z][A-Za-z0-9\-]*")
def tokenize(text: str) -> List[str]:
    """Very simple regex tokenizer: extracts word-like tokens."""
    return TOKEN_PATTERN.findall(text)


# More efficient and sophisticated tokenizers can be integrated here.
# TODO: Replace with a more sophisticated tokenizer if needed, e.g., NLTK, SpaCy, etc.