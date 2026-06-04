from django.contrib import admin
from .models import Department, Course, Student


class CourseInline(admin.TabularInline):
    """Inline admin for courses within department view"""
    model = Course
    extra = 1
    fields = ['code', 'name', 'credits', 'description']
    ordering = ['code']


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course_count']
    search_fields = ['name', 'code']
    inlines = [CourseInline]
    
    def course_count(self, obj):
        count = obj.courses.count()
        return f"{count} course{'s' if count != 1 else ''}"
    course_count.short_description = "Courses"


class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'department', 'credits']
    list_filter = ['department', 'credits']
    search_fields = ['code', 'name', 'department__name']
    ordering = ['department', 'code']
    readonly_fields = ['created_at'] if hasattr(Course, 'created_at') else []
    fieldsets = (
        ('Course Information', {
            'fields': ('department', 'code', 'name', 'credits')
        }),
        ('Additional Details', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )


class StudentAdmin(admin.ModelAdmin):
    list_display = ['get_username', 'department', 'enrollment_no']
    list_filter = ['department']
    search_fields = ['user__username', 'user__email', 'enrollment_no']
    readonly_fields = ['user', 'get_email']
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


admin.site.register(Department, DepartmentAdmin)
admin.site.register(Course, CourseAdmin)
admin.site.register(Student, StudentAdmin)