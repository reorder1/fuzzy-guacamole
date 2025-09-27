from django.contrib import admin

from .models import Batch, Student


@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_number', 'full_name', 'batch')
    search_fields = ('student_number', 'full_name')
    list_filter = ('batch',)
