from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import StudentSignUpForm
from .models import Department, Student, ChatMessage
from books.models import Book
from papers.models import PastPaper, LectureSlide
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.http import JsonResponse
import hashlib

def home(request):
    recent_books = Book.objects.all().select_related('department').order_by('-created_at')[:6]
    recent_papers = PastPaper.objects.all().select_related('department', 'uploaded_by').order_by('-uploaded_at')[:6]
    recent_lectures = LectureSlide.objects.all().select_related('department', 'uploaded_by').order_by('-uploaded_at')[:6]
    lecture_count = LectureSlide.objects.count()
    
    recommended_books = []
    if request.user.is_authenticated and hasattr(request.user, 'student') and request.user.student.department:
        department = request.user.student.department
        recommended_books = Book.objects.filter(department=department).select_related('department').exclude(
            id__in=recent_books.values_list('id', flat=True)
        )[:6]
    
    context = {
        'recent_books': recent_books,
        'recent_papers': recent_papers,
        'recent_lectures': recent_lectures,
        'lecture_count': lecture_count,
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
    total_lectures = LectureSlide.objects.count()

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
        'total_lectures': total_lectures,
        'signup_history': signup_history,
        'department_distribution': department_distribution,
        'department_resources': department_resources,
        'user_list': user_list,
        'recent_books': recent_books,
        'recent_papers': recent_papers,
    }
    return render(request, 'core/dashboard.html', context)


def get_anonymous_details(user):
    # Generates deterministic animal name and gradient avatar color based on user ID
    animals = ["Panda", "Fox", "Koala", "Owl", "Falcon", "Dolphin", "Otter", "Squirrel", "Hedgehog", "Rabbit", "Deer", "Cheetah", "Lion", "Tiger", "Bear", "Wolf", "Beaver", "Badger"]
    adjectives = ["Curious", "Brilliant", "Sleek", "Eager", "Patient", "Swift", "Clever", "Jolly", "Wise", "Kind", "Lively", "Quiet", "Bright", "Sharp"]
    
    hasher = hashlib.md5(f"anon-{user.id}".encode())
    digest = int(hasher.hexdigest(), 16)
    
    adj = adjectives[digest % len(adjectives)]
    animal = animals[(digest // len(adjectives)) % len(animals)]
    num = (digest % 900) + 100
    
    colors = [
        "from-pink-500 to-rose-500",
        "from-purple-500 to-indigo-500",
        "from-blue-500 to-sky-500",
        "from-teal-500 to-emerald-500",
        "from-green-500 to-lime-500",
        "from-yellow-500 to-amber-500",
        "from-orange-500 to-red-500",
        "from-indigo-500 to-violet-500"
    ]
    color = colors[(digest // 10) % len(colors)]
    
    return f"{adj} {animal} #{num}", color


@login_required
def chat_lobby(request):
    departments = Department.objects.all()
    student = getattr(request.user, 'student', None)
    user_dept = student.department if student else None
    
    anon_name, anon_color = get_anonymous_details(request.user)
    
    context = {
        'departments': departments,
        'user_dept': user_dept,
        'anon_name': anon_name,
        'anon_color': anon_color,
    }
    return render(request, 'core/chat.html', context)


@login_required
def get_chat_messages(request):
    dept_id = request.GET.get('dept_id')
    last_id = request.GET.get('last_id', 0)
    
    messages_query = ChatMessage.objects.all().select_related(
        'sender', 'shared_book', 'shared_paper', 'shared_lecture'
    )
    
    if dept_id:
        messages_query = messages_query.filter(department_id=dept_id)
    else:
        messages_query = messages_query.filter(department__isnull=True)
        
    if last_id:
        messages_query = messages_query.filter(id__gt=int(last_id))
        
    messages_query = messages_query.order_by('created_at')[:100]
    
    data = []
    for msg in messages_query:
        sender_anon_name, sender_anon_color = get_anonymous_details(msg.sender)
        
        shared_item = None
        if msg.shared_book:
            shared_item = {
                'id': msg.shared_book.id,
                'type': 'book',
                'title': msg.shared_book.title,
                'detail': f"by {msg.shared_book.author}",
                'icon': '📖',
                'url': f"/viewer/book/{msg.shared_book.id}/"
            }
        elif msg.shared_paper:
            shared_item = {
                'id': msg.shared_paper.id,
                'type': 'paper',
                'title': msg.shared_paper.title,
                'detail': f"{msg.shared_paper.year} - Sem {msg.shared_paper.semester}",
                'icon': '📝',
                'url': f"/viewer/paper/{msg.shared_paper.id}/"
            }
        elif msg.shared_lecture:
            shared_item = {
                'id': msg.shared_lecture.id,
                'type': 'lecture',
                'title': msg.shared_lecture.title,
                'detail': f"Course: {msg.shared_lecture.course_code}",
                'icon': '🛝',
                'url': f"/viewer/lecture/{msg.shared_lecture.id}/"
            }
            
        data.append({
            'id': msg.id,
            'message': msg.message,
            'is_anonymous': msg.is_anonymous,
            'sender_name': sender_anon_name if msg.is_anonymous else msg.sender.username,
            'sender_color': sender_anon_color if msg.is_anonymous else "from-slate-600 to-slate-800",
            'is_self': msg.sender == request.user,
            'created_at': msg.created_at.strftime('%H:%M'),
            'shared_item': shared_item
        })
        
    return JsonResponse({'messages': data})


@login_required
def send_chat_message(request):
    if request.method == 'POST':
        message_text = request.POST.get('message', '').strip()
        is_anon = request.POST.get('is_anonymous') == 'true'
        dept_id = request.POST.get('dept_id')
        
        shared_type = request.POST.get('shared_type')
        shared_id = request.POST.get('shared_id')
        
        if not message_text and not shared_id:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)
            
        dept = None
        if dept_id:
            try:
                dept = Department.objects.get(id=dept_id)
            except Department.DoesNotExist:
                pass
                
        anon_name, _ = get_anonymous_details(request.user)
        
        msg = ChatMessage(
            sender=request.user,
            is_anonymous=is_anon,
            anonymous_name=anon_name if is_anon else "",
            message=message_text,
            department=dept
        )
        
        if shared_type and shared_id:
            try:
                if shared_type == 'book':
                    msg.shared_book = Book.objects.get(id=shared_id)
                elif shared_type == 'paper':
                    msg.shared_paper = PastPaper.objects.get(id=shared_id)
                elif shared_type == 'lecture':
                    msg.shared_lecture = LectureSlide.objects.get(id=shared_id)
            except Exception:
                pass
                
        msg.save()
        return JsonResponse({'status': 'ok'})
        
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def search_shareable_materials(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})
        
    books = Book.objects.filter(Q(title__icontains=q) | Q(author__icontains=q))[:5]
    papers = PastPaper.objects.filter(Q(title__icontains=q) | Q(course_code__icontains=q))[:5]
    lectures = LectureSlide.objects.filter(Q(title__icontains=q) | Q(course_code__icontains=q))[:5]
    
    results = []
    for b in books:
        results.append({'id': b.id, 'type': 'book', 'title': f"📖 [Book] {b.title}", 'detail': f"by {b.author}"})
    for p in papers:
        results.append({'id': p.id, 'type': 'paper', 'title': f"📝 [Paper] {p.title}", 'detail': f"Year {p.year} - {p.course_code}"})
    for l in lectures:
        results.append({'id': l.id, 'type': 'lecture', 'title': f"🛝 [Slide] {l.title}", 'detail': f"Course: {l.course_code}"})
        
    return JsonResponse({'results': results})


@login_required
def view_material(request, type, id):
    material = None
    file_url = ""
    title = ""
    course_code = ""
    department_name = ""
    
    if type == 'book':
        material = get_object_or_404(Book.objects.select_related('department'), id=id)
        file_url = material.pdf_file.url
        title = material.title
        course_code = material.course_code
        department_name = material.department.name
    elif type == 'paper':
        material = get_object_or_404(PastPaper.objects.select_related('department'), id=id)
        file_url = material.pdf_file.url
        title = material.title
        course_code = material.course_code
        department_name = material.department.name
    elif type == 'lecture':
        material = get_object_or_404(LectureSlide.objects.select_related('department'), id=id)
        file_url = material.slide_file.url
        title = material.title
        course_code = material.course_code
        department_name = material.department.name
        
    context = {
        'title': title,
        'file_url': file_url,
        'course_code': course_code,
        'department_name': department_name,
        'material_type': type.capitalize(),
        'material': material
    }
    return render(request, 'core/viewer.html', context)