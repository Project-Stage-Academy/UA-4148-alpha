from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def get_current_user_id(request):
    """
    Extracts current user ID from query params (?user=ID).
    """
    if request.user.is_authenticated:
        return request.user.id
    return None

def index(request):
    """
    Display a list of eligible users to start a chat with.
    """
    current_user_id = get_current_user_id(request)
    users = []

    if request.user.is_authenticated and hasattr(request.user, "role"):
        if request.user.role == "investor":
            users = User.objects.filter(role="startup").exclude(id=current_user_id)

    return render(request, "chat/index.html", {
        "users": users,
        "current_user_id": current_user_id,
    })


def room(request, other_user_id):
    """
    Show the chat room between the logged-in user and another user.
    """
    current_user_id = get_current_user_id(request)

    try:
        other_user = User.objects.get(id=other_user_id)
    except User.DoesNotExist:
        return redirect("index")

    return render(request, "chat/room.html", {
        "other_user_id": other_user.id,
        "current_user_id": current_user_id,
    })
