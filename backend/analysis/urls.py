from django.urls import path

from .views import ExamAnalyticsView

urlpatterns = [
    path('exams/<int:exam_id>/', ExamAnalyticsView.as_view(), name='exam-analytics'),
]
