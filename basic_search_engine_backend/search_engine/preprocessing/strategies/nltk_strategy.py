import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
from ..base import Preprocessor


class NLTKPreprocessor(Preprocessor):
    def __init__(self):
        # Asigurăm descărcarea resurselor o singură dată la inițializare
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)

        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        self.punctuation = set(string.punctuation)

    def process(self, text: str) -> list[str]:
        # Tokenizare profesională și lowercase
        tokens = word_tokenize(text.lower())
        # Filtrare stopwords și semne de punctuație
        filtered = [
            t for t in tokens if t not in self.stop_words and t not in self.punctuation]
        # Lemmatizare (ex: "better" -> "good")
        return [self.lemmatizer.lemmatize(t) for t in filtered]
