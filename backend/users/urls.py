from django.urls import path, include
from users.views import UserViewSet, LogoutView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
]