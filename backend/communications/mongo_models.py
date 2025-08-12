from mongoengine import Document, StringField, DateTimeField, ListField, ReferenceField, CASCADE
import datetime

class Room(Document):
    """
        Represents a chat room between one or more participants.
    """
    meta = {
        'db_alias': 'chat_db',
        'collection': 'rooms',
        'indexes': ['name', 'participants']
    }

    name = StringField(required=True, unique=True)
    participants = ListField(StringField(), default=[])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)

    def add_participant(self, user_id):
        uid = str(user_id)
        if uid not in self.participants:
            self.participants.append(uid)
            self.updated_at = datetime.datetime.utcnow()
            self.save()


class Message(Document):
    """
    Represents a message sent within a chat room.
    """
    meta = {
        'db_alias': 'chat_db',
        'collection': 'messages',
        'indexes': [
            ('room', 'timestamp'),
            '-timestamp'
        ]
    }

    room = ReferenceField(Room, reverse_delete_rule=CASCADE, required=True)
    sender_id = StringField(required=True)
    text = StringField(required=True)
    timestamp = DateTimeField(default=datetime.datetime.utcnow)
