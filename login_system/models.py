from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


# Create your models here.
class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        DOCTOR = "doctor", "Doctor"
        NURSE = "nurse", "Nurse"

    # any one who registered will be admin role by default
    base_role = Role.ADMIN

    role = models.CharField(
        "Role", max_length=50, choices=Role.choices, default=base_role
    )

    # otp = models.CharField("OTP", max_length=4, blank=True, null=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    def is_otp_valid(self):
        if self.otp_created_at is None or self.otp is None:
            return False
        current_time = timezone.now()
        time_difference = current_time - self.otp_created_at
        return self.otp and time_difference.seconds <= 300  # 5 minutes

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class DoctorManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.DOCTOR)


class Doctor(User):
    base_role = User.Role.DOCTOR
    doctor = DoctorManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Doctors"


class DoctorProfile(models.Model):
    # one to one connection to the user table
    user = models.OneToOneField(Doctor, on_delete=models.CASCADE)
    doctor_id = models.IntegerField(null=True, blank=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == "doctor":
            Doctor.objects.create(user=instance)
        elif instance.role == "nurse":
            Nurse.objects.create(user=instance)


class NurseManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.NURSE)


class Nurse(User):
    base_role = User.Role.NURSE
    nurse = NurseManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Nurses"


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
