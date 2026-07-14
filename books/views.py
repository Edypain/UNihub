from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Book
from .forms import BookUploadForm
from core.models import Student

from core.models import Department
from django.core.files.base import ContentFile
from django.utils.text import slugify
import uuid

# Optional PDF rendering dependency (PyMuPDF)
try:
    import fitz
except Exception:
    fitz = None

def book_list(request):
    query = request.GET.get('q', '').strip()
    dept_id = request.GET.get('dept', '').strip()
    
    books = Book.objects.all().select_related('department')
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

            # Ensure PDF is saved and attempt to create a cover image from its first page
            uploaded_pdf = form.cleaned_data.get('pdf_file')
            if uploaded_pdf:
                try:
                    pdf_bytes = uploaded_pdf.read()
                    # Save PDF file to the model filefield
                    book.pdf_file.save(uploaded_pdf.name, ContentFile(pdf_bytes), save=False)

                    # If PyMuPDF is available, render first page to PNG and save as cover_image
                    if fitz is not None:
                        try:
                            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
                            if doc.page_count > 0:
                                page = doc.load_page(0)
                                mat = fitz.Matrix(2, 2)  # render at higher res
                                pix = page.get_pixmap(matrix=mat, alpha=False)
                                img_bytes = pix.tobytes('png')
                                img_name = f"{slugify(book.title)[:40]}-{uuid.uuid4().hex[:8]}.png"
                                book.cover_image.save(img_name, ContentFile(img_bytes), save=False)
                        except Exception:
                            # If rendering fails, continue without a cover image
                            pass
                except Exception:
                    # If reading/saving PDF fails, fall back to normal save (form will still have pdf_file assigned)
                    pass

            # Apply defaults for optional simplified-form fields
            if not book.author or not book.author.strip():
                book.author = 'Unknown Author'

            # Final save
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