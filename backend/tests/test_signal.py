from django.test import TestCase
from communications.mongo_models import Message, Room, MongoNotification

class MessageSignalTestCase(TestCase):
    def setUp(self):
        self.room = Room.objects.create(name="test_room")

    def test_message_creates_notification(self):
        Message.objects.create(
            room=self.room,
            sender_id="1",
            sender_first_name="Julia",
            sender_last_name="V",
            text="Test"
        )
        self.assertEqual(MongoNotification.objects.count(), 1)
