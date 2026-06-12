from django.db import models
from core.models import Department
from core.storage import DynamicRawStorage

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    course_code = models.CharField(max_length=10, blank=True, default='', help_text='Course code like PHY111')
    department = models.ForeignKey(Department, on_delete=models.CASCADE)  # NOT NULL
    tags = models.CharField(max_length=200, blank=True, help_text="Comma-separated tags")
    pdf_file = models.FileField(upload_to='books/', storage=DynamicRawStorage())
    cover_image = models.ImageField(upload_to='covers/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title