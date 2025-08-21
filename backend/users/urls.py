from django.urls import include, path
from rest_framework import routers

from users.views import LogoutView, UserViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
