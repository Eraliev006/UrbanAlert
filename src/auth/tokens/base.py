from abc import ABC, abstractmethod
from typing import Any


class TokenCreator(ABC):
    @abstractmethod
    def create_token(self, payload: dict[str, Any]) -> str:
        raise NotImplemented

    def generate(self, payload: dict[str, Any]) -> str:
        token = self.create_token(payload)
        return token
