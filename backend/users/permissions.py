from rest_framework.permissions import BasePermission
from users.models import UserProfile
class InvestorRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_investor()


class StartupRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_startup()
