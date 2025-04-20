from src.notification import NotifierType, Notifier, EmailNotifier


class NotifierFactory:
    @staticmethod
    def get_notifier(notifier_type: NotifierType) -> Notifier:
        if notifier_type == NotifierType.EMAIL :
            return EmailNotifier()
        else:
            raise ValueError("Unknown notifier type")