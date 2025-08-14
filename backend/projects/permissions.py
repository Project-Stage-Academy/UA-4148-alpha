from rest_framework.permissions import BasePermission

class IsInvestor(BasePermission):
    message = "Only investors can perform this action."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            getattr(request.user.role, 'role', None) == 'investor'
        )
