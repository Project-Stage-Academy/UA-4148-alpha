from rest_framework.permissions import BasePermission


class RolePermission(BasePermission):
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def has_permission(self, request):
        return (
            request.user.is_authenticated
            and request.user.role.role in self.allowed_roles
        )