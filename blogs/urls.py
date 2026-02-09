# blogs/urls.py
from django.urls import path
from . import views

app_name = "blogs"
# blogs/urls.py
urlpatterns = [
    path("", views.blog_list, name="blog_list"),
    path("create/", views.create_blog, name="blog_create"),  # fix here
    path("<int:pk>/", views.blog_detail, name="blog_detail"),
    path("<int:pk>/edit/", views.blog_update, name="blog_update"),
    path("<int:pk>/delete/", views.blog_delete, name="blog_delete"),
]
