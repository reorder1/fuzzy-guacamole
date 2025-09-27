from rest_framework import serializers

from core.serializers import StudentSerializer
from exams.serializers import ExamSerializer
from .models import Scan


class ScanSerializer(serializers.ModelSerializer):
    exam_detail = ExamSerializer(source='exam', read_only=True)
    student_detail = StudentSerializer(source='student', read_only=True)

    class Meta:
        model = Scan
        fields = [
            'id',
            'exam',
            'exam_detail',
            'student',
            'student_detail',
            'image',
            'extracted_student_number',
            'extracted_set_code',
            'answers',
            'confidence',
            'status',
            'issues',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'extracted_student_number',
            'extracted_set_code',
            'answers',
            'confidence',
            'status',
            'issues',
            'created_at',
            'updated_at',
        ]
