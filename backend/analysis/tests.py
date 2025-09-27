from django.test import TestCase

from core.models import Batch, Student
from exams.models import Exam, ExamSet
from exams.services import upsert_score
from .services import compute_exam_analytics


class AnalyticsTests(TestCase):
    def setUp(self):
        batch = Batch.objects.create(name='Batch 1', code='B1')
        self.exam = Exam.objects.create(batch=batch, title='Quiz', num_items=4)
        ExamSet.objects.create(exam=self.exam, set_code='A', answer_key=['A', 'B', 'C', 'D'])
        students = [
            Student.objects.create(batch=batch, student_number=f'{i:03d}', full_name=f'Student {i}')
            for i in range(1, 6)
        ]
        answers_list = [
            ['A', 'B', 'C', 'D'],
            ['A', 'B', 'C', 'A'],
            ['A', 'B', 'D', 'D'],
            ['A', 'C', 'C', 'D'],
            ['B', 'B', 'C', 'D'],
        ]
        for student, answers in zip(students, answers_list):
            upsert_score(exam=self.exam, student=student, set_code='A', answers=answers)

    def test_analytics_metrics(self):
        analytics = compute_exam_analytics(self.exam)
        self.assertEqual(analytics.exam_id, self.exam.id)
        self.assertGreaterEqual(analytics.kr20, 0)
        self.assertEqual(len(analytics.item_stats), 4)
        first_item = analytics.item_stats[0]
        self.assertAlmostEqual(first_item.difficulty, 0.8)
