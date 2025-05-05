from abc import ABC, abstractmethod


class NotificationStrategy(ABC):
    @abstractmethod
    async def notify(self, recipient: str, subject: str, message: str) -> bool:
        pass