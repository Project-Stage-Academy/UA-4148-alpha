from django.apps import AppConfig
from django.conf import settings
from mongoengine import connect


class CommunicationsConfig(AppConfig):
    name = "communications"

    def ready(self):
        connect(
            db=settings.MONGO_DB_NAME,
            host=settings.MONGO_HOST,
            port=int(settings.MONGO_PORT),
            alias="chat_db"
        )
