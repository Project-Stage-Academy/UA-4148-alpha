from django.urls import path

from .views import index, room

urlpatterns = [
    path("", index, name="index"),
    path("room/<int:other_user_id>/", room, name="room"),
]
