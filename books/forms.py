from django import forms
from .models import Book
from core.models import Department

class BookUploadForm(forms.ModelForm):
    # Department field is required, but we will pre‑fill it with the student's department
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=True)

    class Meta:
        model = Book
        fields = ['title', 'author', 'description', 'department', 'tags', 'pdf_file', 'cover_image']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g., python, django, web'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'w-full border rounded p-2 mb-2'})