from pathlib import Path

import cv2
import numpy as np
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from accounts.models import User
from core.models import Batch, Student
from exams.models import Exam, ExamSet, Score
from .models import Scan
from .serializers import ScanSerializer
from .views import ScanViewSet


class ScanProcessingTests(TestCase):
    def setUp(self):
        self.batch = Batch.objects.create(name='Batch 1', code='B1')
        self.student = Student.objects.create(batch=self.batch, student_number='001', full_name='Alice')
        self.exam = Exam.objects.create(batch=self.batch, title='Quiz', num_items=3)
        ExamSet.objects.create(exam=self.exam, set_code='A', answer_key=['A', 'B', 'C'])
        self.user = User.objects.create_user(username='checker', password='pass', role=User.ROLE_CHECKER)

    def _create_test_image(self):
        tmp_dir = Path('media/tests')
        tmp_dir.mkdir(parents=True, exist_ok=True)
        path = tmp_dir / 'scan__student-001__set-A.png'
        cv2.imwrite(str(path), np.zeros((50, 50, 3), dtype=np.uint8))
        path.with_suffix('.json').write_text('{"answers": ["A", "B", "C"]}', encoding='utf-8')
        with path.open('rb') as fh:
            return SimpleUploadedFile(path.name, fh.read(), content_type='image/png')

    def test_scan_processing_creates_score(self):
        data = {'exam': self.exam.id, 'image': self._create_test_image()}
        serializer = ScanSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        viewset = ScanViewSet()
        viewset.request = type('obj', (), {'user': self.user})
        scan = serializer.save()
        viewset._process_scan(scan)
        self.assertEqual(Scan.objects.count(), 1)
        self.assertEqual(Score.objects.count(), 1)
        score = Score.objects.first()
        self.assertEqual(score.raw_score, 3)
        scan.refresh_from_db()
        self.assertEqual(scan.extracted_student_number, '001')
