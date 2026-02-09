from django import forms
from .models import Blog


class BlogForm(forms.ModelForm):

    class Meta:
        model = Blog
        fields = ["title", "content", "status"]

    def __init__(self, *args, **kwargs):

        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        # 👤 Normal Users
        if user and not user.is_staff:
            self.fields["status"].choices = [
                ("draft", "Draft"),
                ("pending", "Submit for Review"),
            ]

        # 👨‍💼 Admin Users
        elif user and user.is_staff:
            self.fields["status"].choices = [
                ("draft", "Draft"),
                ("published", "Published"),
                ("rejected", "Rejected"),
            ]
