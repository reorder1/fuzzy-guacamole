from rest_framework import routers

from .views import ExamSetViewSet, ExamViewSet, ScoreViewSet

router = routers.DefaultRouter()
router.register(r'exams', ExamViewSet)
router.register(r'exam-sets', ExamSetViewSet)
router.register(r'scores', ScoreViewSet)
