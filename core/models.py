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
    
    VIBE_CHOICES = [
        ('none', 'No Vibe'),
        ('cramming', '🔥 Cramming'),
        ('confused', '😵‍💫 Confused'),
        ('acing', '🚀 Acing it'),
        ('chill', '☕ Chill'),
        ('tired', '😴 Tired'),
        ('curious', '🤔 Curious'),
    ]
    vibe = models.CharField(max_length=20, choices=VIBE_CHOICES, default='none')
    upvotes_count = models.IntegerField(default=0)
    
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


# ──────────────────────────────────────────────────────────────────
# COLLABO — Student Group Collaboration
# ──────────────────────────────────────────────────────────────────

import random
import string

def _generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))


class StudyGroup(models.Model):
    name        = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    department  = models.ForeignKey(
        Department, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='study_groups'
    )
    owner       = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_groups'
    )
    members     = models.ManyToManyField(
        User, through='GroupMembership', related_name='study_groups'
    )
    invite_code = models.CharField(
        max_length=8, unique=True, default=_generate_invite_code
    )
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-created_at']


class GroupMembership(models.Model):
    ROLE_CHOICES = [('owner', 'Owner'), ('member', 'Member')]
    group  = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='memberships')
    user   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='memberships')
    role   = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} → {self.group.name} ({self.role})"


class GroupTask(models.Model):
    STATUS_CHOICES = [
        ('todo',       '📝 To Do'),
        ('inprogress', '⚡ In Progress'),
        ('done',       '✅ Done'),
    ]
    group       = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='tasks')
    title       = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status      = models.CharField(max_length=15, choices=STATUS_CHOICES, default='todo')
    assigned_to = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_tasks'
    )
    due_date    = models.DateField(null=True, blank=True)
    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    created_at  = models.DateTimeField(auto_now_add=True)
    order       = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.status}] {self.title}"

    class Meta:
        ordering = ['order', 'created_at']


class GroupDocument(models.Model):
    group          = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='documents')
    title          = models.CharField(max_length=200)
    url            = models.URLField(blank=True)
    shared_book    = models.ForeignKey(
        'books.Book', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='group_shares'
    )
    shared_paper   = models.ForeignKey(
        'papers.PastPaper', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='group_shares'
    )
    shared_lecture = models.ForeignKey(
        'papers.LectureSlide', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='group_shares'
    )
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_documents')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-added_at']


class GroupMessage(models.Model):
    group      = models.ForeignKey(StudyGroup, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages')
    text       = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.text[:40]}"

    class Meta:
        ordering = ['created_at']
