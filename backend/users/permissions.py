from rest_framework.permissions import BasePermission


class InvestorRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.role == "investor"


class StartupRolePermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role.role == "startup"
