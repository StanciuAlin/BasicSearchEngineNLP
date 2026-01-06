import spacy
from ..base import Preprocessor

class SpacyPreprocessor(Preprocessor):
    def __init__(self, model="en_core_web_sm"):
        # Încărcăm modelul și dezactivăm componentele inutile (ner, parser) pentru viteză
        self.nlp = spacy.load(model, disable=['parser', 'ner'])
        # Adăugăm stopwords din spaCy
        self.stop_words = self.nlp.Defaults.stop_words

    def process(self, text: str) -> list[str]:
        if not text:
            return []
            
        # Procesăm textul prin pipeline-ul spaCy
        doc = self.nlp(text.lower())
        
        tokens = []
        for token in doc:
            # Filtrare profesionistă:
            # 1. Să nu fie stopword
            # 2. Să nu fie semn de punctuație
            # 3. Să nu fie spațiu gol
            # 4. Să aibă lungime > 2
            if not token.is_stop and not token.is_punct and not token.is_space:
                lemma = token.lemma_.strip()
                if len(lemma) > 2:
                    tokens.append(lemma)
                    
        return tokens