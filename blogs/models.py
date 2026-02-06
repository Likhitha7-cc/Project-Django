from django.conf import settings
from django.db import models


class Blog(models.Model):

    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    CATEGORY_CHOICES = (
        ("Technology", "Technology"),
        ("Education", "Education"),
        ("Health", "Health"),
        ("Travel", "Travel"),
        ("Business", "Business"),
        ("Lifestyle", "Lifestyle"),
        ("Sports", "Sports"),
        ("General", "General"),
    )

    title = models.CharField(max_length=255)
    content = models.TextField()

    # ✅ NEW FIELD FOR AI CATEGORY
    category = models.CharField(
        max_length=50,
        default="General",
        blank=True
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs",
    )

    image = models.ImageField(
        upload_to="blog_images/", blank=True, null=True
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="draft"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
