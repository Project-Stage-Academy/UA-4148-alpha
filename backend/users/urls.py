from django.urls import path, include
from users.views import UserViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('users/login/', UserViewSet.as_view({'post': 'login'}), name='user-login'), # Maybe this code is not neededbecause we use ViewSet with @action and connect via DefaultRouter?
    path('users/register/', UserViewSet.as_view({'post': 'register'}), name='user-register'), # Maybe this code is not neededbecause we use ViewSet with @action and connect via DefaultRouter?
]