from django.test import TestCase

from core.models import Batch, Student
from .models import Exam, ExamSet, Score
from .services import grade_answers, recompute_exam_scores, upsert_score


class ScoringTests(TestCase):
    def setUp(self):
        self.batch = Batch.objects.create(name='Batch 1', code='B1')
        self.student = Student.objects.create(batch=self.batch, student_number='001', full_name='Alice')
        self.exam = Exam.objects.create(batch=self.batch, title='Midterm', num_items=3)
        self.exam_set = ExamSet.objects.create(exam=self.exam, set_code='A', answer_key=['A', 'B', 'C'])

    def test_grade_answers(self):
        result = grade_answers(['A', 'C', 'C'], self.exam_set.answer_key)
        self.assertEqual(result.raw_score, 2)
        self.assertAlmostEqual(result.percent, (2 / 3) * 100)
        self.assertEqual(result.breakdown[1]['correct'], False)

    def test_upsert_score(self):
        score = upsert_score(exam=self.exam, student=self.student, set_code='A', answers=['A', 'B', 'C'])
        self.assertEqual(score.raw_score, 3)
        score = upsert_score(exam=self.exam, student=self.student, set_code='A', answers=['A', 'B', 'D'])
        self.assertEqual(score.raw_score, 2)
        self.assertEqual(Score.objects.count(), 1)

    def test_recompute(self):
        upsert_score(exam=self.exam, student=self.student, set_code='A', answers=['A', 'B', 'D'])
        Score.objects.filter(student=self.student).update(breakdown=[
            {'item': 1, 'answer': 'A', 'key': 'A', 'correct': True},
            {'item': 2, 'answer': 'B', 'key': 'B', 'correct': True},
            {'item': 3, 'answer': 'D', 'key': 'C', 'correct': False},
        ])
        updated = recompute_exam_scores(self.exam)
        self.assertEqual(updated, 1)
        self.assertEqual(Score.objects.get().raw_score, 2)
