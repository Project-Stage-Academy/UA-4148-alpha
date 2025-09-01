import logging
from django.shortcuts import render

# Get logger for this module
logger = logging.getLogger(__name__)


def index(request):
    logger.info(f"Chat index page accessed by user: {request.user.username if request.user.is_authenticated else 'anonymous'}")
    try:
        return render(request, "chat/index.html")
    except Exception as e:
        logger.error(f"Error rendering chat index page: {str(e)}", exc_info=True)
        raise


def room(request, room_name):
    logger.info(f"Chat room '{room_name}' accessed by user: {request.user.username if request.user.is_authenticated else 'anonymous'}")
    try:
        return render(request, "chat/room.html", {"room_name": room_name})
    except Exception as e:
        logger.error(f"Error rendering chat room '{room_name}': {str(e)}", exc_info=True)
        raise
