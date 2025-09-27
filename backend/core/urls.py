from rest_framework import routers

from .views import BatchViewSet, StudentViewSet

router = routers.DefaultRouter()
router.register(r'batches', BatchViewSet)
router.register(r'students', StudentViewSet)
