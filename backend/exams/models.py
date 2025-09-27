from django.db import models

from core.models import Batch, Student


class Exam(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='exams')
    title = models.CharField(max_length=255)
    num_items = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} ({self.batch.code})"


class ExamSet(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sets')
    set_code = models.CharField(max_length=10)
    answer_key = models.JSONField(default=list)

    class Meta:
        unique_together = ('exam', 'set_code')
        ordering = ['set_code']

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.exam.title} - {self.set_code}"


class Score(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scores')
    set_code = models.CharField(max_length=10)
    raw_score = models.PositiveIntegerField(default=0)
    percent = models.FloatField(default=0.0)
    breakdown = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['exam', 'student'], name='unique_exam_student_score'),
        ]
        ordering = ['-updated_at']

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.exam_id}:{self.student_id} = {self.raw_score}"
