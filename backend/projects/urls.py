from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ProjectViewSet, SavedProjectsList

router = DefaultRouter()
router.register(r"", ProjectViewSet, basename="project")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "investor/saved-projects/",
        SavedProjectsList.as_view(),
        name="investor-saved-projects",
    ),
    path(
        "users/<int:user_id>/investors/<int:investor_id>/saved-startups/",
        SavedProjectsList.as_view(),
        name="user-investor-saved-startups",
    ),
    path(
        "startups/<int:startup_id>/unsave/",
        ProjectViewSet.as_view(),
        name="startup-unsave",
    ),
]
