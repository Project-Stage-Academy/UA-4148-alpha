from django.urls import path, include
from users.views import UserViewSet, LogoutView
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/login/', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('users/register/', UserViewSet.as_view({'post': 'register'}), name='user-register'),
]