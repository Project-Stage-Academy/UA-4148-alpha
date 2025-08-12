from django.urls import path, include
from users.views import UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('users/login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('users/register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
]