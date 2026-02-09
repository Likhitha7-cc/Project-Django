from django.conf import settings
from django.db import models


class Blog(models.Model):

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('pending', 'Pending Review'),
        ('published', 'Published'),
        ('rejected', 'Rejected'),
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

    # ✅ AI Category
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="General",
        blank=True
    )

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blogs",
    )

    image = models.ImageField(
        upload_to="blog_images/",
        blank=True,
        null=True
    )

    # ✅ Status must allow 'published' (9 chars)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft"
    )

    # ✅ Role-based approval fields
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="approved_blogs"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
