from ..base import Preprocessor
from ..core.normalizer import normalize
from ..core.stemmer import simple_stem


class CustomPreprocessor(Preprocessor):
    def process(self, text: str) -> list[str]:
        # Folosește logica ta: lowercasing + regex + manual stopwords
        tokens = normalize(text)
        # Aplică stemmer-ul de tip suffix stripping
        return [simple_stem(t) for t in tokens]
