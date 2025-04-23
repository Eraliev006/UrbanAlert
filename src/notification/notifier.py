from abc import ABC, abstractmethod


class Notifier(ABC):
    @abstractmethod
    def notify(self, to_user: str, otp_code: int):
        raise NotImplemented