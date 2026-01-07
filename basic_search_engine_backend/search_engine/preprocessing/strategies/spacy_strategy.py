import spacy
from ..base import Preprocessor

"""
Module: spacy_strategy.py
Description: Implements a high-precision NLP preprocessing strategy using the 
SpaCy library. This strategy focuses on contextual lemmatization and advanced 
linguistic filtering.
"""
class SpacyPreprocessor(Preprocessor):
    """
    A professional NLP preprocessor powered by SpaCy.
    
    This strategy utilizes SpaCy's pre-trained language models to perform 
    lemmatization, which identifies the dictionary root of words (e.g., 
    "organized" -> "organize"). It is optimized for accuracy and handles 
    complex linguistic structures better than rule-based stemmers.
    """
    
    def __init__(self, model="en_core_web_sm"):
        """
        Initializes the SpaCy pipeline with optimized settings.
        
        Args:
            model (str): The name of the SpaCy language model to load. 
                         Defaults to the lightweight English model.
        
        Note:
            Components such as the 'parser' and 'ner' (Named Entity Recognition) 
            are disabled to maximize processing speed, as they are not 
            required for basic tokenization and lemmatization.
        """
        
        # Load the model and disable unnecessary components for performance
        self.nlp = spacy.load(model, disable=['parser', 'ner'])
        # Retrieve the default stop words for the loaded language
        self.stop_words = self.nlp.Defaults.stop_words

    def process(self, text: str) -> list[str]:
        """
        Transforms raw text into a list of high-quality lemmas.
        
        The pipeline executes the following steps:
        1. Case folding (lowercasing).
        2. Professional filtering: removes stop words, punctuation, and whitespace.
        3. Lemmatization: extracts the base form of each token.
        4. Length constraint: excludes tokens with 2 or fewer characters to reduce noise.
        
        Args:
            text (str): The input string to be normalized.
            
        Returns:
            list[str]: A collection of cleaned, lemmatized tokens.
            
        Complexity:
            O(L), where L is the length of the text. Although linear, this strategy 
            is computationally more expensive than regex-based methods due to 
            the underlying linguistic models.
        """
        
        if not text:
            return []
            
        # Process the text through the optimized SpaCy pipeline
        doc = self.nlp(text.lower())
        
        tokens = []
        for token in doc:
            # Multi-tier filtering logic:
            # 1. Exclude stop words (common words with low information value)
            # 2. Exclude punctuation marks
            # 3. Exclude whitespace tokens
            if not token.is_stop and not token.is_punct and not token.is_space:
                # Extract and clean the lemma
                lemma = token.lemma_.strip()
                # 4. Final noise reduction: minimum character length check
                if len(lemma) > 2:
                    tokens.append(lemma)
                    
        return tokens