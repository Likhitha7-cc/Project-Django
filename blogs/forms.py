# blogs/forms.py
from django import forms
from .models import Blog


class BlogForm(forms.ModelForm):
    """
    Form to create/edit blogs.
    """
    class Meta:
        model = Blog
        fields = ("title", "content", "image", "status")