from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentSignUpForm
from .models import Department, Student
from books.models import Book
from papers.models import PastPaper

def home(request):
    recent_books = Book.objects.all().order_by('-created_at')[:6]
    recent_papers = PastPaper.objects.all().order_by('-uploaded_at')[:6]
    
    recommended_books = []
    if request.user.is_authenticated and hasattr(request.user, 'student') and request.user.student.department:
        department = request.user.student.department
        recommended_books = Book.objects.filter(department=department).exclude(
            id__in=recent_books.values_list('id', flat=True)
        )[:6]
    
    context = {
        'recent_books': recent_books,
        'recent_papers': recent_papers,
        'recommended_books': recommended_books,
    }
    return render(request, 'core/home.html', context)

def signup(request):
    if request.method == 'POST':
        form = StudentSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = StudentSignUpForm()
    return render(request, 'core/signup.html', {'form': form})

@login_required
def edit_profile(request):
    student, created = Student.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        department_id = request.POST.get('department')
        if department_id:
            try:
                student.department = Department.objects.get(id=department_id)
                student.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('home')
            except Department.DoesNotExist:
                messages.error(request, 'Invalid department selected.')
        else:
            messages.error(request, 'Please select a department.')
    departments = Department.objects.all()
    return render(request, 'core/edit_profile.html', {'student': student, 'departments': departments})