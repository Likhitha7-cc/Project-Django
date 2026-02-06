# blogs/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render, redirect
from .ai_utils import detect_blog_category


from .forms import BlogForm
from .models import Blog


def blog_list(request):
    """
    List blogs with pagination and search on title.

    - Non-authenticated or non-admin users see only published blogs.
    - Admins see all blogs.
    """
    blogs = Blog.objects.all()

    # Filter by published for non-admin
    if not request.user.is_authenticated or getattr(request.user, "role", "user") != "admin":
        blogs = blogs.filter(status="published")

    # Search by title via ?q=
    query = request.GET.get("q")
    if query:
        blogs = blogs.filter(title__icontains=query)

    paginator = Paginator(blogs, 5)  # 5 blogs per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "blogs": page_obj,
        "query": query or "",
    }
    return render(request, "blog_list.html", context)


def blog_detail(request, pk):
    """
    Show a single blog.
    Draft blogs are only visible to the author or admin.
    """
    blog = get_object_or_404(Blog, pk=pk)

    if blog.status != "published":
        if not request.user.is_authenticated:
            raise Http404("Blog not found")
        if request.user != blog.author and getattr(request.user, "role", "user") != "admin":
            raise Http404("Blog not found")

    context = {
        "blog": blog,
    }
    return render(request, "blog_detail.html", context)


@login_required
def blog_create(request):
    """
    Create a new blog. Author is the logged-in user.
    AI automatically assigns category.
    """
    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user

            # 🤖 AI CATEGORY DETECTION
            try:
                blog.category = detect_blog_category(
                    blog.title,
                    blog.content
                )
            except Exception:
                blog.category = "General"

            blog.save()

            messages.success(request, "Blog created successfully.")
            return redirect("blogs:blog_detail", pk=blog.pk)
    else:
        form = BlogForm()

    return render(request, "blog_form.html", {"form": form, "form_title": "Create Blog"})


@login_required
def blog_update(request, pk):
    """
    Update existing blog.
    Only the author or an admin can update.
    """
    blog = get_object_or_404(Blog, pk=pk)

    if request.user != blog.author and getattr(request.user, "role", "user") != "admin":
        return HttpResponseForbidden("You are not allowed to edit this blog.")

    if request.method == "POST":
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            form.save()
            messages.success(request, "Blog updated successfully.")
            return redirect("blogs:blog_detail", pk=blog.pk)
    else:
        form = BlogForm(instance=blog)

    return render(request, "blog_form.html", {"form": form, "form_title": "Edit Blog"})


@login_required
def blog_delete(request, pk):
    """
    Delete a blog. Only author or admin.
    Deletion is done via POST (e.g. from a button on blog_detail page).
    """
    blog = get_object_or_404(Blog, pk=pk)

    if request.user != blog.author and getattr(request.user, "role", "user") != "admin":
        return HttpResponseForbidden("You are not allowed to delete this blog.")

    if request.method == "POST":
        blog.delete()
        messages.success(request, "Blog deleted successfully.")
        return redirect("blogs:blog_list")

    # If not POST, redirect back to detail
    return redirect("blogs:blog_detail", pk=pk)