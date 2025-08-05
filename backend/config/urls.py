from django.contrib import admin
from django.urls import path, include
from users.views import UserViewSet
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views as authtoken_views

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/api-token-auth/', authtoken_views.obtain_auth_token, name='api-token-auth'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
