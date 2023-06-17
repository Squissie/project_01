from django.urls import path
from . import views

path("reset_password_request/", views.reset_password_request, name="reset_password_request"),