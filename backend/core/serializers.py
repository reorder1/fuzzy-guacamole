from rest_framework import serializers

from .models import Batch, Student


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'name', 'code', 'created_at']
        read_only_fields = ['id', 'created_at']


class StudentSerializer(serializers.ModelSerializer):
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = Student
        fields = ['id', 'batch', 'batch_name', 'student_number', 'full_name', 'email', 'created_at']
        read_only_fields = ['id', 'created_at']
