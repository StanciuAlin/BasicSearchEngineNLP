# basic_search_engine_backend/search_engine/preprocessing/stemmer.py
# Third step in text preprocessing: stemming.

# Educational simple stemmer implementation.
def simple_stem(token: str) -> str:
    # suffix stripping stemmer
    for suffix in ("ing", "ed", "s"):
        if token.endswith(suffix) and len(token) > len(suffix) + 2:
            return token[: -len(suffix)]
    return token

# More advanced stemmer implementations can be added here.