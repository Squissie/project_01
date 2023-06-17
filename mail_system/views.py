from django.contrib.auth import authenticate, login
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
import random
import math
from django.contrib.auth.decorators import login_required
from login_system.models import User
from django.utils import timezone


def reset_password_request(request):
    if request.method == "POST":
        username = request.POST.get("username")
        user = User.objects.filter(username=username).first()
        if user:
            request.session["reset_password_username"] = username
            return redirect("otp_form")
        else:
            messages.error(request, "Invalid username")

    return render(request, "reset_password_template/reset_password_request.html")


def otp_form(request):
    reset_password_username = request.session.get("reset_password_username")
    if not reset_password_username:
        return redirect("reset_password_request")

    user = User.objects.filter(username=reset_password_username).first()
    if not user:
        messages.error(request, "Invalid username")
        return redirect("reset_password_request")

    if request.method == "POST":
        otp = request.POST.get("otp")
        if user.otp == otp:
            otp_created_at = user.otp_created_at
            current_time = timezone.now()
            if current_time > otp_created_at + timezone.timedelta(minutes=15):
                # OTP is no longer valid
                messages.error(request, "Expired OTP")
            else:
                # OTP matches and is still valid, store user in session and redirect to resetPassword page
                request.session["reset_password_user_id"] = user.id
                request.session.pop("reset_password_username")
                user.otp = None
                user.otp_created_at = None
                user.save()
                return redirect("reset_password")
        else:
            messages.error(request, "Incorrect OTP")

    if request.GET.get("resend_otp"):
        # Generate OTP and send to user's email
        try:
            otp = generateOTP()
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()
            message = f"Hi {user.username},<br><br>You recently requested to reset your password for your account. Use the OTP below to verify your identity and complete the process:<br><br>OTP: <b> {otp} </b><br><br>Please note that this OTP is valid for only 5 minutes.\n\nIf you did not request a password reset, please ignore this email.<br><br>Thanks,<br><br>COVIDVisionX"
            send_mail(
                "Reset Password Request:",
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
                html_message=message,
            )
            messages.success(request, "OTP has been resent to your email.")
        except User.DoesNotExist:
            messages.error(request, "Invalid user")
            return redirect("reset_password_request")

    return render(request, "reset_password_template/otp_form.html", {"user": user})


def reset_password(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            user = request.user
        else:
            user_id = request.session.get("reset_password_user_id")
            if not user_id:
                messages.error(
                    request, "Session expired. Please request a new password reset."
                )
                return redirect("reset_password_request")
            user = User.objects.filter(id=user_id).first()
            if not user:
                messages.error(request, "Invalid user")
                return redirect("reset_password_request")

        new_password = request.POST["new_password"]
        confirm_password = request.POST["confirm_password"]
        if new_password != confirm_password:
            messages.error(request, "Passwords do not match")
            return render(request, "reset_pwd.html")
        user.set_password(new_password)
        try:
            user.save()
        except Exception as e:
            print(f"Error saving user: {e}")
            messages.error(request, "An error occurred while resetting your password")
            return render(request, "reset_pwd.html")
        messages.success(request, "Password successfully reset")
        return redirect("login")

    return render(request, "reset_pwd.html")


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP
