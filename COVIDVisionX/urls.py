"""svm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from svmApp import views
from django.conf.urls.static import static
from django.conf import settings
from login_system import views as login_views
from django.urls import include
from mail_system import views as mail_views
from admin_user import views as admin_views

## This file defines URLs that can be accessed

urlpatterns = [
    #path for login
    path("", login_views.login_view, name="login"),
    path("createUser", login_views.create_user, name="createUser"),
    path("resetPassword/", mail_views.reset_password, name="reset_password"),
    path("reset_password_request/",mail_views.reset_password_request,name="reset_password_request",),
    path("reset_password_request/otp_form/", mail_views.otp_form, name="otp_form"),
    #path for doctor/nurse
    path("home", views.home, name="home"),
    path("addPatient", views.addPatient, name="addPatient"),
    path("addImage/<int:consultation_id>", views.addImage, name="addImage"),
    path("patientRecords", views.patientRecords, name="patientRecords"),
    path("patientRecords/<int:patient_id>", views.patientProfile, name="patientProfile"),
    path("patientRecordsAdd/<int:patient_id>", views.patientProfileAdd, name="patientProfileAdd"),
    path("editConsultation/<int:consultation_id>", views.editConsultation, name="editConsultation"),
    #path for admin
    path('admin_home/', admin_views.UserTableView.as_view(), name='admin_home'),
    path('users/', admin_views.UserTableView.as_view(), name='user_table'),
    path('users/<int:pk>/suspend/', admin_views.UserSuspendView.as_view(), name='user_suspend'),
    path('users/<int:pk>/activate/', admin_views.UserActivateView.as_view(), name='user_activate'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
