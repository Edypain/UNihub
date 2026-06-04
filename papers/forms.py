from django import forms
from .models import PastPaper

class PastPaperUploadForm(forms.ModelForm):
    class Meta:
        model = PastPaper
        fields = ['title', 'year', 'semester', 'pdf_file']