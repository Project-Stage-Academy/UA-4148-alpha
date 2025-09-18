from mongoengine import signals
from .mongo_models import Message, MongoNotification


def create_message_notification(sender, document, **kwargs):
    if kwargs.get('created', False):
        MongoNotification.objects.create(
            message_id=str(document.id),
            room_name=document.room.name,
            sender_name=document.sender_first_name,
        )
        print(f"Notification created for message {document.id}")

signals.post_save.connect(create_message_notification, sender=Message)
