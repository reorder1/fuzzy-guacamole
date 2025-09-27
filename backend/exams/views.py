import csv
import io

from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrChecker, IsAdminOrReadOnly
from core.models import Student
from .models import Exam, ExamSet, Score
from .serializers import ExamSerializer, ExamSetSerializer, ScoreSerializer
from .services import recompute_exam_scores, upsert_score


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.select_related('batch').all()
    serializer_class = ExamSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.query_params.get('batch')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        return queryset

    @action(detail=True, methods=['post'], permission_classes=[IsAdmin])
    def recompute(self, request, pk=None):
        exam = self.get_object()
        updated = recompute_exam_scores(exam)
        return Response({'updated': updated})

    @action(detail=True, methods=['get'], permission_classes=[IsAdminOrChecker])
    def export(self, request, pk=None):
        exam = self.get_object()
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=exam-{exam.pk}-scores.csv'
        writer = csv.writer(response)
        writer.writerow(['student_number', 'full_name', 'set_code', 'raw_score', 'percent'])
        for score in exam.scores.select_related('student'):
            writer.writerow([
                score.student.student_number,
                score.student.full_name,
                score.set_code,
                score.raw_score,
                score.percent,
            ])
        return response


class ExamSetViewSet(viewsets.ModelViewSet):
    queryset = ExamSet.objects.select_related('exam').all()
    serializer_class = ExamSetSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        exam_id = self.request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        return queryset


class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.select_related('exam', 'student').all()
    serializer_class = ScoreSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [IsAdminOrChecker]
        else:
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        exam_id = self.request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAdmin])
    def bulk_upsert(self, request, *args, **kwargs):
        exam_id = request.data.get('exam')
        set_code = request.data.get('set_code')
        answers_map = request.data.get('answers', {})
        exam = Exam.objects.get(pk=exam_id)
        updated = 0
        for student_id, answers in answers_map.items():
            student = Student.objects.get(pk=student_id)
            upsert_score(exam=exam, student=student, set_code=set_code, answers=answers)
            updated += 1
        return Response({'processed': updated}, status=status.HTTP_200_OK)
