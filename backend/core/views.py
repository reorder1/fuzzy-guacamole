import csv
import io

from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from accounts.permissions import IsAdmin, IsAdminOrReadOnly
from .models import Batch, Student
from .serializers import BatchSerializer, StudentSerializer


class BatchViewSet(viewsets.ModelViewSet):
    queryset = Batch.objects.all().order_by('-created_at')
    serializer_class = BatchSerializer
    permission_classes = [IsAdminOrReadOnly]


class StudentViewSet(viewsets.ModelViewSet):
    queryset = Student.objects.select_related('batch').all()
    serializer_class = StudentSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        batch_id = self.request.query_params.get('batch')
        if batch_id:
            queryset = queryset.filter(batch_id=batch_id)
        return queryset

    @action(detail=False, methods=['post'], permission_classes=[IsAdmin])
    def import_csv(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'file is required'}, status=400)
        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        created = 0
        for row in reader:
            batch_id = row.get('batch') or request.data.get('batch')
            if not batch_id:
                continue
            student, is_created = Student.objects.update_or_create(
                batch_id=batch_id,
                student_number=row.get('student_number') or row.get('student_no'),
                defaults={
                    'full_name': row.get('full_name') or row.get('name', ''),
                    'email': row.get('email', ''),
                },
            )
            if is_created:
                created += 1
        return Response({'created': created})
