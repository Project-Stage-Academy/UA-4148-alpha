from django.urls import path
from .views import SubscriptionCreateView

urlpatterns = [
    path(
        "<int:project_id>/subscribe/",
        SubscriptionCreateView.as_view(),
        name="subscribe-to-project"
    ),
]
