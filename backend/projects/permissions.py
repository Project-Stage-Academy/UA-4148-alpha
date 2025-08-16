# projects/permissions.py
from rest_framework.permissions import BasePermission

class IsInvestor(BasePermission):
    message = "User must be an investor."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # 1) Якщо у користувача є пов'язаний InvestorProfile (OneToOne/ForeignKey reverse accessor)
        if hasattr(user, "investorprofile"):
            try:
                return user.investorprofile is not None
            except Exception:
                return False

        # 2) Резервна перевірка по ролі (якщо у тебе є поле role на User)
        role = getattr(user, "role", None)
        if role is not None:
            # role може бути об'єктом з атрибутом 'role' або рядком — обробляємо обидва випадки
            role_name = getattr(role, "role", None) or (role if isinstance(role, str) else None)
            if role_name and str(role_name).lower() == "investor":
                return True

        return False
