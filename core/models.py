from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ['name']


class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    code = models.CharField(max_length=20, help_text="e.g., PHY111, MTH201")
    name = models.CharField(max_length=200, help_text="e.g., Physics 1, Calculus 2")
    description = models.TextField(blank=True, null=True, help_text="Optional course description")
    credits = models.IntegerField(default=3, help_text="Number of credit units")
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        ordering = ['department', 'code']
        unique_together = ['department', 'code']


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    enrollment_no = models.CharField(max_length=20, unique=True, blank=True, null=True)

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        ordering = ['-user']


class ChatMessage(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    is_anonymous = models.BooleanField(default=True)
    anonymous_name = models.CharField(max_length=100, blank=True)
    message = models.TextField(blank=True)
    
    # Optional channel grouping by department
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_messages')
    
    # Shared resources
    shared_book = models.ForeignKey('books.Book', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_shares')
    shared_paper = models.ForeignKey('papers.PastPaper', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_shares')
    shared_lecture = models.ForeignKey('papers.LectureSlide', on_delete=models.SET_NULL, null=True, blank=True, related_name='chat_shares')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        name = self.anonymous_name if self.is_anonymous else self.sender.username
        return f"{name}: {self.message[:30]}"

    class Meta:
        ordering = ['created_at']