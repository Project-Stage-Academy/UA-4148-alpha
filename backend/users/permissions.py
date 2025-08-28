from rest_framework.permissions import BasePermission
from users.models import UserProfile


class InvestorRolePermission(BasePermission):
    """
    Custom permission to allow access only to users with the 'investor' role.

    Grants permission if the user is authenticated and their role is 'investor'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_investor()


class StartupRolePermission(BasePermission):
    """
    Custom permission to allow access only to users with the 'startup' role.

    Grants permission if the user is authenticated and their role is 'startup'.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_startup()
