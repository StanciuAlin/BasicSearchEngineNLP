# basic_search_engine_backend/search_engine/preprocessing/normalizer.py
# Second step in text preprocessing: normalization.
# Combines lowercasing, tokenization, and stopword removal.

# preprocessing/core/normalizer.py
from .tokenizer import tokenize
from .stopwords import STOPWORDS


# TODO: Extend the actual regex or use string.punctuation for more advanced normalization


def normalize(text: str):
    # lowercase + tokenization + stopword removal
    tokens = tokenize(text.lower())
    return [t for t in tokens if t not in STOPWORDS]
