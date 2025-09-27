from __future__ import annotations

import uuid
from pathlib import Path

from django.db import models

from core.models import Student
from exams.models import Exam


def scan_upload_path(instance, filename):
    ext = Path(filename).suffix
    return f"scans/{instance.exam_id}/{uuid.uuid4()}{ext}"


class Scan(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PROCESSED = 'processed'
    STATUS_NEEDS_REVIEW = 'needs_review'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_PROCESSED, 'Processed'),
        (STATUS_NEEDS_REVIEW, 'Needs Review'),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='scans')
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, related_name='scans', null=True, blank=True)
    image = models.ImageField(upload_to=scan_upload_path)
    extracted_student_number = models.CharField(max_length=50, blank=True)
    extracted_set_code = models.CharField(max_length=10, blank=True)
    answers = models.JSONField(default=list, blank=True)
    confidence = models.FloatField(default=0.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    issues = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def mark_processed(
        self,
        *,
        student: Student | None,
        extracted_student_number: str,
        set_code: str,
        answers,
        confidence: float,
        issues=None,
    ):
        self.student = student
        self.extracted_student_number = extracted_student_number
        self.extracted_set_code = set_code
        self.answers = answers
        self.confidence = confidence
        self.status = self.STATUS_PROCESSED if not issues else self.STATUS_NEEDS_REVIEW
        self.issues = issues or []
        self.save(update_fields=['student', 'extracted_student_number', 'extracted_set_code', 'answers', 'confidence', 'status', 'issues', 'updated_at'])
