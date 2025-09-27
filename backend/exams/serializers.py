from typing import List

from rest_framework import serializers

from core.serializers import StudentSerializer
from .models import Exam, ExamSet, Score


class ExamSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamSet
        fields = ['id', 'exam', 'set_code', 'answer_key']


class ExamSerializer(serializers.ModelSerializer):
    sets = ExamSetSerializer(many=True, read_only=True)

    class Meta:
        model = Exam
        fields = ['id', 'batch', 'title', 'num_items', 'created_at', 'sets']
        read_only_fields = ['id', 'created_at', 'sets']


class ScoreSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=Score._meta.get_field('student').remote_field.model.objects.all(), source='student', write_only=True)

    class Meta:
        model = Score
        fields = ['id', 'exam', 'student', 'student_id', 'set_code', 'raw_score', 'percent', 'breakdown', 'created_at', 'updated_at']
        read_only_fields = ['id', 'raw_score', 'percent', 'breakdown', 'created_at', 'updated_at']

    def validate(self, attrs):
        exam = attrs.get('exam') or getattr(self.instance, 'exam', None)
        set_code = attrs.get('set_code') or getattr(self.instance, 'set_code', None)
        if exam and set_code and not exam.sets.filter(set_code=set_code).exists():
            raise serializers.ValidationError({'set_code': 'Invalid set code for this exam.'})
        return attrs
