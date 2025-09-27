from django.contrib import admin

from .models import Exam, ExamSet, Score


class ExamSetInline(admin.TabularInline):
    model = ExamSet
    extra = 0


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'batch', 'num_items', 'created_at')
    list_filter = ('batch',)
    inlines = [ExamSetInline]


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'raw_score', 'percent', 'set_code')
    list_filter = ('exam', 'set_code')
    search_fields = ('student__student_number', 'student__full_name')
