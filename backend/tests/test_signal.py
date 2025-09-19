from django.test import TestCase
import mongoengine
from communications.mongo_models import Message, Room, MongoNotification

class MessageSignalTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        mongoengine.connect(
            db="test_db",
            host="mongomock://localhost"
        )

    @classmethod
    def tearDownClass(cls):
        mongoengine.disconnect()
        super().tearDownClass()

    def setUp(self):
        self.room = Room.objects.create(name="test_room")

    def test_message_creates_notification(self):
        Message.objects.create(
            room=self.room,
            sender_id="1",
            sender_first_name="Julia",
            sender_last_name="V",
            text="Test",
        )
        self.assertEqual(MongoNotification.objects.count(), 1)
