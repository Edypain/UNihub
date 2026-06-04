from django import forms
from django.core.validators import RegexValidator
from .models import PastPaper, LectureSlide

course_code_validator = RegexValidator(
    regex=r'^[A-Za-z]{2,4}\d{3}$',
    message='Course code must be in the format ABC123, e.g. PHY111.',
)

class PastPaperUploadForm(forms.ModelForm):
    course_code = forms.CharField(
        required=True,
        max_length=10,
        validators=[course_code_validator],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., PHY111'}),
        help_text='Enter the course code for this past paper.',
    )

    class Meta:
        model = PastPaper
        fields = ['title', 'year', 'semester', 'course_code', 'pdf_file']


class LectureSlideUploadForm(forms.ModelForm):
    course_code = forms.CharField(
        required=True,
        max_length=10,
        validators=[course_code_validator],
        widget=forms.TextInput(attrs={'placeholder': 'e.g., PHY111'}),
        help_text='Enter the course code for this lecture slide.',
    )

    class Meta:
        model = LectureSlide
        fields = ['title', 'description', 'course_code', 'slide_file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }