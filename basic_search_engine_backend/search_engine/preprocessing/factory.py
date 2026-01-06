from .strategies.custom_strategy import CustomPreprocessor
from .strategies.nltk_strategy import NLTKPreprocessor
from .strategies.spacy_strategy import SpacyPreprocessor


class PreprocessorFactory:
    def __init__(self):
        # Cache pentru instanțe (Eficiență: nu re-inițializăm NLTK la fiecare query)
        self._instances = {
            "custom": CustomPreprocessor(),
            "pro": NLTKPreprocessor(),
            "spacy": SpacyPreprocessor()
        }

    def get_preprocessor(self, mode: str):
        return self._instances.get(mode, self._instances["custom"])


# Instanță globală pentru a fi importată în app.py sau engine.py
factory = PreprocessorFactory()


def get_preprocessor(mode: str):
    return factory.get_preprocessor(mode)
