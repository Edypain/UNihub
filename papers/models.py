from django.db import models
from core.models import Department
from django.contrib.auth.models import User

class PastPaper(models.Model):
    title = models.CharField(max_length=200)
    year = models.IntegerField()
    semester = models.CharField(max_length=20)
    course_code = models.CharField(max_length=10, blank=True, default='', help_text='Course code like PHY111')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    pdf_file = models.FileField(upload_to='papers/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.year})"