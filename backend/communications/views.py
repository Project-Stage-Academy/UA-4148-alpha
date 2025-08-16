from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def get_current_user_id(request):
    """
    Extracts current user ID from query params (?user=ID).
    Fallback to default ID=1 for now if not provided.
    """
    try:
        return int(request.GET.get("user", 1))
    except (ValueError, TypeError):
        return 1

def index(request):
    """
    Display a list of users to start a chat with.
    """
    current_user_id = get_current_user_id(request)
    users = User.objects.exclude(id=current_user_id)

    return render(request, "chat/index.html", {
        "users": users,
        "current_user_id": current_user_id,
    })


def room(request, other_user_id):
    """
    Show the chat room for the selected user.
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
