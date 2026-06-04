from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentSignUpForm
from .models import Department, Student
from books.models import Book
from papers.models import PastPaper
from django.contrib.auth.models import User
from django.db.models import Count
from django.db.models.functions import TruncDate

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

@login_required
def analytics_dashboard(request):
    # Enforce staff-only access
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to access the analytics dashboard.')
        return redirect('home')

    # 1. KPI Key Metrics
    total_users = User.objects.count()
    total_students = Student.objects.count()
    total_departments = Department.objects.count()
    total_books = Book.objects.count()
    total_papers = PastPaper.objects.count()

    # 2. User Signups Over Time (Grouped by Date)
    signups_by_date = (
        User.objects.annotate(date=TruncDate('date_joined'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')
    )
    signup_history = [
        {
            'date': entry['date'].strftime('%Y-%m-%d') if entry['date'] else 'Unknown',
            'count': entry['count']
        }
        for entry in signups_by_date
    ]

    # 3. Department Student Distribution
    dept_stats = (
        Department.objects.annotate(student_count=Count('student'))
        .values('name', 'code', 'student_count')
        .order_by('-student_count')
    )
    department_distribution = [
        {
            'name': dept['name'],
            'code': dept['code'],
            'student_count': dept['student_count']
        }
        for dept in dept_stats
    ]

    # 4. Department Resource Distribution (Books & Past Papers)
    resource_stats = (
        Department.objects.annotate(
            book_count=Count('book', distinct=True),
            paper_count=Count('pastpaper', distinct=True)
        )
        .values('name', 'code', 'book_count', 'paper_count')
        .order_by('name')
    )
    department_resources = [
        {
            'name': res['name'],
            'code': res['code'],
            'book_count': res['book_count'],
            'paper_count': res['paper_count'],
            'total_resources': res['book_count'] + res['paper_count']
        }
        for res in resource_stats
    ]

    # 5. User List Table with details
    all_users = User.objects.annotate(
        paper_count=Count('pastpaper', distinct=True)
    ).select_related('student__department').order_by('-date_joined')

    user_list = []
    for u in all_users:
        dept_name = u.student.department.name if hasattr(u, 'student') and u.student.department else 'N/A'
        user_list.append({
            'username': u.username,
            'email': u.email or 'No email provided',
            'is_staff': u.is_staff,
            'date_joined': u.date_joined.strftime('%Y-%m-%d %H:%M'),
            'department': dept_name,
            'paper_count': u.paper_count
        })

    # 6. Recent Activity Streams
    recent_books = Book.objects.select_related('department').order_by('-created_at')[:5]
    recent_papers = PastPaper.objects.select_related('department', 'uploaded_by').order_by('-uploaded_at')[:5]

    context = {
        'total_users': total_users,
        'total_students': total_students,
        'total_departments': total_departments,
        'total_books': total_books,
        'total_papers': total_papers,
        'signup_history': signup_history,
        'department_distribution': department_distribution,
        'department_resources': department_resources,
        'user_list': user_list,
        'recent_books': recent_books,
        'recent_papers': recent_papers,
    }
    return render(request, 'core/dashboard.html', context)