from django.db import models


class Batch(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.code})"


class Student(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='students')
    student_number = models.CharField(max_length=50)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['batch', 'student_number'], name='unique_student_per_batch'),
        ]
        ordering = ['student_number']

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.student_number} - {self.full_name}"
