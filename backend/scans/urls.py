from rest_framework import routers

from .views import ScanViewSet

router = routers.DefaultRouter()
router.register(r'scans', ScanViewSet)
