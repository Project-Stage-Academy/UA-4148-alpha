from django.urls import  path
from .views import UserLoginView

urlpatterns = [
    path('signin/', UserLoginView.as_view(), name='signin'),
]
