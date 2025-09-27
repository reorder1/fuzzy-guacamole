from __future__ import annotations

from django.http import FileResponse
from rest_framework import status, viewsets
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrChecker
from core.models import Student
from exams.services import upsert_score
from .models import Scan
from .serializers import ScanSerializer
from omr.overlay import build_overlay
from omr.reader import OMRProcessingError, process_scan


class ScanViewSet(viewsets.ModelViewSet):
    queryset = Scan.objects.select_related('exam', 'student').all()
    serializer_class = ScanSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ['destroy']:
            permission_classes = [IsAdmin]
        else:
            permission_classes = [IsAdminOrChecker]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        exam_id = self.request.query_params.get('exam')
        if exam_id:
            queryset = queryset.filter(exam_id=exam_id)
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        scan: Scan = serializer.save()
        self._process_scan(scan)

    def _process_scan(self, scan: Scan) -> None:
        try:
            result = process_scan(scan.image.path)
        except OMRProcessingError as exc:  # pragma: no cover - defensive
            scan.status = Scan.STATUS_NEEDS_REVIEW
            scan.issues = ['processing_error', str(exc)]
            scan.save(update_fields=['status', 'issues', 'updated_at'])
            return

        student = None
        if result.student_number:
            student = Student.objects.filter(batch=scan.exam.batch, student_number=result.student_number).first()
            if not student:
                scan.issues.append('student_not_found')
        if student:
            upsert_score(exam=scan.exam, student=student, set_code=result.set_code, answers=result.answers)
        scan.mark_processed(
            student=student,
            extracted_student_number=result.student_number,
            set_code=result.set_code,
            answers=result.answers,
            confidence=result.confidence,
            issues=scan.issues + result.issues if scan.issues else result.issues,
        )

    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        scan = self.get_object()
        student_id = request.data.get('student')
        set_code = request.data.get('set_code')
        answers = request.data.get('answers', [])
        student = Student.objects.filter(pk=student_id).first()
        if not student:
            return Response({'detail': 'Student not found'}, status=status.HTTP_400_BAD_REQUEST)
        upsert_score(exam=scan.exam, student=student, set_code=set_code, answers=answers)
        scan.mark_processed(
            student=student,
            extracted_student_number=student.student_number,
            set_code=set_code,
            answers=answers,
            confidence=1.0,
            issues=[],
        )
        return Response(ScanSerializer(scan, context=self.get_serializer_context()).data)

    @action(detail=True, methods=['get'])
    def overlay(self, request, pk=None):
        scan = self.get_object()
        overlay_path = build_overlay(scan.image.path, scan.answers or [])
        return FileResponse(open(overlay_path, 'rb'), content_type='image/png')
