import logging
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

# Get logger for this module
logger = logging.getLogger(__name__)


def index(request):
    """
    Render the chat landing page.
    """
    logger.info(f"Chat index page accessed by user: {request.user.username if request.user.is_authenticated else 'anonymous'}")
    try:
        return render(request, "chat/index.html")
    except Exception as e:
        logger.error(f"Error rendering chat index page: {str(e)}", exc_info=True)
        raise


def room(request, other_user_id):
    """
    Render the chat room page.
    Pass both current user ID and the selected other user ID.
    """
    logger.info(f"Chat room accessed by user: {request.user.username if request.user.is_authenticated else 'anonymous'} with other_user_id: {other_user_id}")
    try:
        return render(
            request,
            "chat/room.html",
            {
                "other_user_id": other_user_id,
                "current_user_id": request.user.id,
            },
        )
    except Exception as e:
        logger.error(f"Error rendering chat room with other_user_id {other_user_id}: {str(e)}", exc_info=True)
        raise
