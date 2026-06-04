from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Department

class StudentSignUpForm(UserCreationForm):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        help_text="Select your department"
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'department')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # The signal will create a Student profile automatically,
            # but we need to update its department.
            student = user.student
            student.department = self.cleaned_data.get('department')
            student.save()
        return user