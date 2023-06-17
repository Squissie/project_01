from django.shortcuts import render, redirect
from django.contrib import messages
from login_system.models import User, Doctor, Nurse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from .login_checks import *
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            print(user.role) # type:ignore user.role field does exist in all user subclasses
            messages.success(request, "You have successfully logged in!")
            if n := request.GET.get("next"):
                return redirect(n)
            elif user.role == User.Role.ADMIN: # type:ignore user.role field does exist in all user subclasses
                return redirect("admin_home")
            else:
                return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")
    else:
        if request.user.is_authenticated:
            logout(request)
        return render(request, "login.html")


@user_passes_test(check_admin)
def create_user(request):
    if request.method == "POST":
        user_type = request.POST.get("user-type")
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        ## check if any field is empty
        if not (user_type and username and email and password and confirm_password):
            messages.error(request, "All fields are required!")
            return redirect("createUser")
        
        try:
            validate_password(password)
        except ValidationError as e:
            messages.warning(request, ' '.join(e.messages))
            return redirect("createUser")

        ## check if user with the same username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect("createUser")

        ## check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect("createUser")

        ## create new user based on the usertype to decide whether to use Doctor or Nurse model
        if user_type == "doctor":
            user = Doctor.objects.create_user( # type:ignore create_user function inherited from User
                username=username, email=email, password=password
            )
            user.save()
        elif user_type == "nurse":
            user = Nurse.objects.create_user( # type:ignore create_user function inherited from User
                username=username, email=email, password=password
            )
            user.save()
        else:
            user = User.objects.create_user( # type:ignore create_user function inherited from User
                username=username, email=email, password=password
            )
            user.save()

        messages.success(request, "Account created successfully!")
        return redirect("createUser")

    return render(request, "createUser.html")
