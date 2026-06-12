from django.contrib import admin

# hdjd models here.
from .models import PastPaper, LectureSlide

@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'year', 'semester', 'department', 'uploaded_by', 'uploaded_at')
    list_filter = ('department', 'year', 'semester')
    search_fields = ('title', 'course_code', 'department__name', 'uploaded_by__username')

@admin.register(LectureSlide)
class LectureSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'course_code', 'department', 'uploaded_by', 'uploaded_at')
    list_filter = ('department',)
    search_fields = ('title', 'course_code', 'department__name', 'uploaded_by__username')
