import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from books.models import Book
from papers.models import PastPaper
from core.models import Department

print("Departments:")
for dept in Department.objects.all():
    print(f"- {dept.name} ({dept.code})")

print("\nBooks:")
for book in Book.objects.all():
    print(f"- {book.title} by {book.author} (Department: {book.department.code})")

print("\nPast Papers:")
for paper in PastPaper.objects.all():
    print(f"- {paper.title} ({paper.year}, Department: {paper.department.code})")
