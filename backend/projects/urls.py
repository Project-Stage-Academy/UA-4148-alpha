from django.urls import path
from .views import SubscriptionCreateView

urlpatterns = [
    path(
        "api/v1/projects/<int:project_id>/subscribe/",
        SubscriptionCreateView.as_view(),
        name="subscribe-to-project"
    ),
]
