from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, View
from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model
from login_system.models import User
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

## This file handles pages for the admins

## login validation for class-based views
def login_required_decorator(view_func):
    decorated_view_func = login_required(view_func)
    return decorated_view_func

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == User.Role.ADMIN # type:ignore django adds request field automatically

## Page showing all registered users
@method_decorator(login_required, name='dispatch')
class UserTableView(AdminRequiredMixin, ListView):
    model = get_user_model()
    template_name = "admin_template/user_table.html"
    context_object_name = "users"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        search_username = self.request.GET.get("search_username")
        search_user_type = self.request.GET.get("search_user_type")

        if search_username:
            queryset = queryset.filter(username__icontains=search_username)

        if search_user_type:
            queryset = queryset.filter(role=search_user_type)

        return queryset

## Button link for suspending user
@method_decorator(login_required, name='dispatch')
class UserSuspendView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), pk=kwargs["pk"])
        if user.id == request.user.id: # type:ignore django adds id field automatically
            messages.warning(request, "You cannot suspend yourself!")
            return redirect("user_table")
        user.is_active = not user.is_active
        user.save()
        if user.is_active:
            messages.success(request, "User has been activated.")
        else:
            messages.success(request, "User has been suspended.")
        return redirect("user_table")

## Button link for reactivating suspended user
@method_decorator(login_required, name='dispatch')
class UserActivateView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(get_user_model(), pk=kwargs["pk"])
        user.is_active = True
        user.save()
        messages.success(request, "User has been activated.")
        return redirect("user_table")
