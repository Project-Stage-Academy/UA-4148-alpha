import logging
from rest_framework.permissions import BasePermission

# Get logger for this module
logger = logging.getLogger(__name__)


class InvestorRolePermission(BasePermission):
    """
    Custom permission to allow access only to users with the 'investor' role.

    Grants permission if the user is authenticated and their role is 'investor'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.warning(f"Permission denied: User not authenticated for {request.method} {request.path}")
            return False
        
        if not hasattr(request.user, 'role') or not request.user.role:
            logger.warning(f"Permission denied: User ID {request.user.id} has no role assigned for {request.method} {request.path}")
            return False
        
        if request.user.role.role != "investor":
            logger.warning(f"Permission denied: User ID {request.user.id} with role '{request.user.role.role}' attempted to access investor-only endpoint {request.method} {request.path}")
            return False
        
        logger.debug(f"Permission granted: User ID {request.user.id} with investor role accessing {request.method} {request.path}")
        return True


class StartupRolePermission(BasePermission):
    """
    Custom permission to allow access only to users with the 'startup' role.

    Grants permission if the user is authenticated and their role is 'startup'.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            logger.warning(f"Permission denied: User not authenticated for {request.method} {request.path}")
            return False
        
        if not hasattr(request.user, 'role') or not request.user.role:
            logger.warning(f"Permission denied: User ID {request.user.id} has no role assigned for {request.method} {request.path}")
            return False
        
        if request.user.role.role != "startup":
            logger.warning(f"Permission denied: User ID {request.user.id} with role '{request.user.role.role}' attempted to access startup-only endpoint {request.method} {request.path}")
            return False
        
        logger.debug(f"Permission granted: User ID {request.user.id} with startup role accessing {request.method} {request.path}")
        return True
