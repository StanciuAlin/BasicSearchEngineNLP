"""
Module: stopwords.py
Description: Defines a static collection of high-frequency words that carry 
minimal semantic weight in the context of Information Retrieval.
"""

# A curated set of common English words (stop-words) to be filtered out
# during the normalization process. Removing these terms reduces the
# noise in the inverted index and focuses the ranking algorithms on
# descriptive, high-information keywords.
STOPWORDS = {
    "the", "a", "an", "of", "and", "or", "is", "are", "to",
    "for", "in", "on", "that", "this", "it", "using", "be",
    "can", "often", "about", "basic", "as", "with", "by"
}
