from abc import ABC, abstractmethod
from typing import List


class Preprocessor(ABC):
    @abstractmethod
    def process(self, text: str) -> List[str]:
        """Metodă abstractă pentru procesarea textului."""
        pass
