from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from .forms import BookUploadForm
from core.models import Student

from core.models import Department

def book_list(request):
    query = request.GET.get('q', '').strip()
    dept_id = request.GET.get('dept', '').strip()
    
    books = Book.objects.all()
    departments = Department.objects.all()
    recommended = []

    # Filter books
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(tags__icontains=query) |
            Q(description__icontains=query)
        )
    
    if dept_id:
        books = books.filter(department_id=dept_id)
    else:
        # Reorder to show student's department first if no specific department filter is applied
        if request.user.is_authenticated:
            student, created = Student.objects.get_or_create(user=request.user)
            if student.department:
                dept_books = books.filter(department=student.department)
                other_books = books.exclude(department=student.department)
                books = list(dept_books) + list(other_books)

    book_id = request.GET.get('book_id')
    if book_id:
        try:
            current_book = Book.objects.get(id=book_id)
            tags = current_book.tags.split(',')
            if tags and tags[0]:
                recommended = Book.objects.filter(
                    Q(tags__icontains=tags[0]) | Q(department=current_book.department)
                ).exclude(id=current_book.id)[:5]
        except Book.DoesNotExist:
            pass

    context = {
        'books': books,
        'recommended': recommended,
        'departments': departments,
    }
    return render(request, 'books/list.html', context)

@login_required
def upload_book(request):
    student, created = Student.objects.get_or_create(user=request.user)
    if student.department is None:
        messages.error(request, 'You must set your department before uploading a book. Please update your profile.')
        return redirect('edit_profile')

    if request.method == 'POST':
        form = BookUploadForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.department = student.department
            book.save()
            messages.success(request, 'Book uploaded successfully!')
            return redirect('book_list')
    else:
        initial = {'department': student.department}
        form = BookUploadForm(initial=initial)
    return render(request, 'books/upload.html', {'form': form})

def view_pdf(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    return render(request, 'books/view_pdf.html', {'book': book})