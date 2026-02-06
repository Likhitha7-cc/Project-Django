# adminpanel/views.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import CustomUser


@login_required
def user_list(request):
    """
    Admin panel: list all users and allow:
      - activate/deactivate users
      - change user role
    """
    if request.user.role != "admin":
        return HttpResponseForbidden("Admins only.")

    users = CustomUser.objects.all().order_by("-date_joined")

    if request.method == "POST":
        user_id = request.POST.get("user_id")
        action = request.POST.get("action")
        target_user = get_object_or_404(CustomUser, id=user_id)

        # Prevent admin from deactivating themselves accidentally
        if target_user == request.user and action == "toggle_active":
            messages.error(request, "You cannot deactivate your own account.")
            return redirect("adminpanel:user_list")

        if action == "toggle_active":
            target_user.is_active = not target_user.is_active
            target_user.save()
            state = "activated" if target_user.is_active else "deactivated"
            messages.success(request, f"User {target_user.username} {state}.")
        elif action == "change_role":
            new_role = request.POST.get("role")
            valid_roles = [choice[0] for choice in CustomUser.ROLE_CHOICES]
            if new_role in valid_roles:
                target_user.role = new_role
                target_user.save()
                messages.success(
                    request,
                    f"Role for {target_user.username} changed to {new_role}.",
                )
            else:
                messages.error(request, "Invalid role selected.")

        return redirect("adminpanel:user_list")

    context = {
        "users": users,
        "role_choices": CustomUser.ROLE_CHOICES,
    }
    return render(request, "user_list.html", context)