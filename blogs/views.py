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

    - Public users see only published blogs
    - Staff/Admin users see all blogs
    """

    blogs = Blog.objects.all().order_by("-created_at")

    # Role Based Visibility
    if not request.user.is_authenticated or not request.user.is_staff:
        blogs = blogs.filter(status="published")

    # Search
    query = request.GET.get("q")
    if query:
        blogs = blogs.filter(title__icontains=query)

    paginator = Paginator(blogs, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "blog_list.html",
        {
            "blogs": page_obj,
            "page_obj": page_obj,
            "query": query or "",
        },
    )


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
def create_blog(request):
    if request.method == "POST":
        form = BlogForm(request.POST, user=request.user)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            # Role based control
            if request.user.is_staff:
                blog.status = "published"
            else:
                blog.status = "pending"
            blog.save()
            messages.success(request, "Blog created successfully.")
            return redirect("blogs:blog_detail", pk=blog.pk)
    else:
        form = BlogForm(user=request.user)
    
    return render(request, "blog_form.html", {"form": form})


from django.utils import timezone


@login_required
def blog_update(request, pk):

    blog = get_object_or_404(Blog, pk=pk)

    # Permission check
    if request.user != blog.author and not request.user.is_staff:
        return HttpResponseForbidden("You are not allowed to edit this blog.")

    if request.method == "POST":

        # ✅ VERY IMPORTANT — pass user into form
        form = BlogForm(
            request.POST,
            request.FILES,
            instance=blog,
            user=request.user
        )

        if form.is_valid():
            blog = form.save(commit=False)

            action = request.POST.get("action")

            # 👨‍💼 ADMIN ACTIONS
            if request.user.is_staff:

                if action == "publish":
                    blog.status = "published"
                    blog.approved_by = request.user
                    blog.approved_at = timezone.now()

                elif action == "reject":
                    blog.status = "rejected"
                    blog.approved_by = request.user
                    blog.approved_at = timezone.now()

                elif action == "draft":
                    blog.status = "draft"

            # 👤 NORMAL USER ACTIONS
            else:

                if action == "submit":
                    blog.status = "pending"

                elif action == "draft":
                    blog.status = "draft"

                # 🔒 SECURITY BLOCK (very important)
                if blog.status not in ["draft", "pending"]:
                    blog.status = "pending"

            blog.save()

            messages.success(request, "Blog updated successfully.")
            return redirect("blogs:blog_detail", pk=blog.pk)

    else:

        # ✅ VERY IMPORTANT — pass user into form
        form = BlogForm(instance=blog, user=request.user)

    return render(
        request,
        "blog_form.html",
        {
            "form": form,
            "form_title": "Edit Blog",
            "blog": blog,
        },
    )


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

