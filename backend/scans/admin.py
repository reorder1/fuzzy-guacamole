from django.contrib import admin

from .models import Scan


@admin.register(Scan)
class ScanAdmin(admin.ModelAdmin):
    list_display = ('exam', 'student', 'status', 'confidence', 'created_at')
    list_filter = ('status', 'exam')
    search_fields = ('extracted_student_number',)
