from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from accounts.views import AuthTokenObtainPairView, AuthTokenRefreshView, MeView
from core.urls import router as core_router
from exams.urls import router as exams_router
from scans.urls import router as scans_router
from analysis.urls import urlpatterns as analysis_urls

router = routers.DefaultRouter()
router.registry.extend(core_router.registry)
router.registry.extend(exams_router.registry)
router.registry.extend(scans_router.registry)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/token/', AuthTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', AuthTokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', MeView.as_view(), name='auth_me'),
    path('api/', include(router.urls)),
    path('api/analysis/', include((analysis_urls, 'analysis'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
