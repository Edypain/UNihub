from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PastPaper, LectureSlide
from .forms import PastPaperUploadForm, LectureSlideUploadForm
from core.models import Student

from core.models import Department
from django.db.models import Q

def paper_list(request):
    departments = Department.objects.all()
    # Get distinct years sorted descending
    available_years = PastPaper.objects.values_list('year', flat=True).distinct().order_by('-year')

    if request.user.is_authenticated:
        student, created = Student.objects.get_or_create(user=request.user)
        papers = PastPaper.objects.all().select_related('department', 'uploaded_by').order_by('-year')

        query = request.GET.get('q', '').strip()
        dept_id = request.GET.get('dept', '').strip()
        year_val = request.GET.get('year', '').strip()

        # Apply filters if provided
        if query:
            papers = papers.filter(title__icontains=query)
        if dept_id:
            papers = papers.filter(department_id=dept_id)
        if year_val:
            try:
                papers = papers.filter(year=int(year_val))
            except ValueError:
                pass

        # Default to student's department if no filter was explicitly queried
        if not (query or dept_id or year_val) and student.department:
            papers = papers.filter(department=student.department)
    else:
        papers = PastPaper.objects.none()

    context = {
        'papers': papers,
        'departments': departments,
        'available_years': available_years,
    }
    return render(request, 'papers/list.html', context)

@login_required
def upload_paper(request):
    student, created = Student.objects.get_or_create(user=request.user)
    if student.department is None:
        messages.error(request, 'You must set your department before uploading a paper. Please update your profile.')
        return redirect('edit_profile')

    if request.method == 'POST':
        form = PastPaperUploadForm(request.POST, request.FILES)
        if form.is_valid():
            paper = form.save(commit=False)
            paper.uploaded_by = request.user
            paper.department = student.department
            paper.save()
            messages.success(request, 'Past paper uploaded successfully!')
            return redirect('paper_list')
    else:
        form = PastPaperUploadForm()
    return render(request, 'papers/upload.html', {'form': form})


@login_required
def lecture_list(request):
    departments = Department.objects.all()
    lectures = LectureSlide.objects.all().select_related('department', 'uploaded_by').order_by('-uploaded_at')

    if request.user.is_authenticated:
        student, created = Student.objects.get_or_create(user=request.user)
        query = request.GET.get('q', '').strip()
        dept_id = request.GET.get('dept', '').strip()

        if query:
            lectures = lectures.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(course_code__icontains=query)
            )
        if dept_id:
            lectures = lectures.filter(department_id=dept_id)

        if not (query or dept_id) and student.department:
            lectures = lectures.filter(department=student.department)
    else:
        lectures = LectureSlide.objects.none()

    context = {
        'lectures': lectures,
        'departments': departments,
    }
    return render(request, 'lectures/list.html', context)


@login_required
def upload_lecture(request):
    student, created = Student.objects.get_or_create(user=request.user)
    if student.department is None:
        messages.error(request, 'You must set your department before uploading a lecture slide. Please update your profile.')
        return redirect('edit_profile')

    if request.method == 'POST':
        form = LectureSlideUploadForm(request.POST, request.FILES)
        if form.is_valid():
            lecture = form.save(commit=False)
            lecture.uploaded_by = request.user
            lecture.department = student.department
            lecture.save()
            messages.success(request, 'Lecture slide uploaded successfully!')
            return redirect('lecture_list')
    else:
        form = LectureSlideUploadForm()
    return render(request, 'lectures/upload.html', {'form': form})


def view_pdf(request, paper_id):
    paper = get_object_or_404(PastPaper, id=paper_id)
    return render(request, 'papers/view_pdf.html', {'paper': paper})