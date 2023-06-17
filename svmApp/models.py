from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import date
from django.utils.timezone import now

from login_system.models import User

## This file determines the database setup

class PatientModel(models.Model):
    FEMALE = "F"
    MALE = "M"
    GENDER_CHOICES = (
        (FEMALE, "Female"),
        (MALE, "Male"),
    )

    firstName = models.CharField("First Name", max_length=100)
    lastName = models.CharField("Last Name", max_length=100)
    gender = models.CharField("Gender", max_length=1, choices=GENDER_CHOICES)
    dateofbirth = models.DateField(
        "Date of Birth",
        validators=[
            MinValueValidator(date(1900, 1, 1)),
            MaxValueValidator(now().date()),
        ],
    )
    ## Patients can be assigned to doctors to show up in their homepage queue
    assigned_user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        ...

    def __str__(self):
        return f"{self.firstName} {self.lastName}"


class ConsultationModel(models.Model):
    patient = models.ForeignKey(PatientModel, on_delete=models.CASCADE)
    datetime = models.DateField(
        "Appointment",
        validators=[
            MinValueValidator(date(1900, 1, 1)),
            MaxValueValidator(date(2100, 1, 1)),
        ],
        default=now().date(),
    )
    symptoms = models.CharField("Symptoms", max_length=255, null=True)
    diagnosis = models.CharField("Diagnosis", max_length=255, null=True)
    medication = models.CharField("Medication", max_length=255, null=True)
    treatment = models.CharField("Treatment", max_length=255, null=True)

    class Meta:
        ordering = ["-datetime"]


class ImageModel(models.Model):
    ## link to patient for convenience
    patient = models.ForeignKey(PatientModel, on_delete=models.CASCADE)
    consultation = models.ForeignKey(ConsultationModel, on_delete=models.DO_NOTHING)
    image = models.ImageField("Image", upload_to="images")
    cam = models.ImageField("Image", upload_to="images", null=True)
    title = models.CharField("Image Title", max_length=50)
    result = models.CharField("Evaluation", max_length=255, null=True)
    comments = models.CharField("Comments", max_length=255, null=True)

    class Meta:
        ...
