from ..base import Preprocessor
from ..core.normalizer import normalize
from ..core.stemmer import simple_stem


class CustomPreprocessor(Preprocessor):
    def process(self, text: str) -> list[str]:
        # Obținem lista de cuvinte întregi deja izolate prin regex
        tokens = normalize(text)

        # Aplicăm stemmer-ul pe fiecare cuvânt întreg.
        # Deoarece indexul inversat folosește aceste chei, "car" și "carpet"
        # vor fi mapate la chei diferite în dicționar.
        return [simple_stem(t) for t in tokens if t]
