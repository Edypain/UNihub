from django import forms
from django.core.validators import RegexValidator
from .models import Book
from core.models import Department

course_code_validator = RegexValidator(
    regex=r'^[A-Za-z]{2,4}\d{3}$',
    message='Course code must be in the format ABC123, e.g. PHY111.',
)

class BookUploadForm(forms.ModelForm):
    # Department field is required, but we will pre‑fill it with the student's department
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)
    course_code = forms.CharField(
        required=False,
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'e.g., PHY111'}),
        help_text='Enter the course code for this book (optional).',
    )

    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'course_code', 'department', 'tags', 'pdf_file', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g., python, django, web'}),
        }

    cover_image = forms.ImageField(required=False, help_text='Optional cover image for the book.')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make author optional in the simplified upload flow
        self.fields['author'].required = False
        self.fields['author'].initial = 'Unknown Author'
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full border rounded p-2 mb-2'})