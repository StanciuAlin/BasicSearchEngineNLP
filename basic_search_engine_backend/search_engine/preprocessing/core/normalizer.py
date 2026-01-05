# basic_search_engine_backend/search_engine/preprocessing/normalizer.py
# Second step in text preprocessing: normalization.
# Combines lowercasing, tokenization, and stopword removal.

# preprocessing/core/normalizer.py
import re


def normalize(text: str) -> list[str]:
    # Pasul 1: Conversie la litere mici pentru uniformitate
    text = text.lower()

    # Pasul 2: Tokenizare strictă pentru cuvinte întregi.
    # Folosim \b (word boundary) pentru a ne asigura că izolăm cuvântul de punctuație.
    # re.findall(r'\b\w+\b', ...) extrage doar secvențele alfanumerice complete.
    tokens = re.findall(r'\b\w+\b', text)

    return tokens
