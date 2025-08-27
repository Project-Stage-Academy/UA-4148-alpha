from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    """
    Render the chat landing page.
    """
    return render(request, "chat/index.html")


def room(request, other_user_id):
    """
    Render the chat room page.
    Pass both current user ID and the selected other user ID.
    """
    return render(
        request,
        "chat/room.html",
        {
            "other_user_id": other_user_id,
            "current_user_id": request.user.id,
        },
    )
