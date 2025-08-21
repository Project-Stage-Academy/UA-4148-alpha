from django.urls import path

from communications.views import index, room

urlpatterns = [
    path("", views.index, name="index"),
    path("room/<int:other_user_id>/", views.room, name="room"),
]
