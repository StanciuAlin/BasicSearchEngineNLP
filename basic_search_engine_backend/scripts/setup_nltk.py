import nltk

"""
Script: nltk_setup.py
Description: Initial configuration script for the NLTK (Natural Language Toolkit) library.
This script ensures that all necessary corpora and pre-trained models are available 
locally before the search engine starts processing text.
"""

# 1. 'punkt' & 'punkt_tab': Essential for the Punkt Sentence Tokenizer.
# These models divide text into a list of sentences or words by using an
# unsupervised algorithm to learn abbreviations and sentence starters.
nltk.download('punkt')
nltk.download('punkt_tab')

# 2. 'stopwords': A collection of high-frequency words (e.g., 'the', 'is', 'in')
# that are typically filtered out during indexing to focus on terms with
# higher semantic value.
nltk.download('stopwords')

# 3. 'wordnet' & 'omw-1.4': Lexical databases for the English language.
# These are used by the WordNetLemmatizer to resolve words to their
# dictionary roots (e.g., 'better' -> 'good', 'rocks' -> 'rock').
nltk.download('wordnet')
nltk.download('omw-1.4')

"""
Note: These downloads are typically required only once per environment. 
In a production environment, it is recommended to wrap these in a try-except 
block or verify existing resources to avoid redundant network calls.
"""
