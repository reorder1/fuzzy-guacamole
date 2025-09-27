from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import IsAdminOrChecker
from exams.models import Exam
from .services import compute_exam_analytics


class ExamAnalyticsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrChecker]

    def get(self, request, exam_id: int):
        exam = Exam.objects.get(pk=exam_id)
        analytics = compute_exam_analytics(exam)
        data = {
            'exam_id': analytics.exam_id,
            'kr20': analytics.kr20,
            'average_score': analytics.average_score,
            'average_percent': analytics.average_percent,
            'item_stats': [
                {
                    'item': stat.item,
                    'difficulty': stat.difficulty,
                    'discrimination_index': stat.discrimination_index,
                    'point_biserial': stat.point_biserial,
                }
                for stat in analytics.item_stats
            ],
        }
        return Response(data)
