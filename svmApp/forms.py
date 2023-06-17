from django import forms
from .models import *
from django.utils.timezone import now

## This file determines boundary layer between database and user input

## Form to create new patient
class PatientEditForm(forms.ModelForm):
    class Meta:
        model = PatientModel
        exclude = (
            "image",
            "assigned_user",
        )
        widgets = {
            "dateofbirth": forms.SelectDateWidget(years=range(1900, now().year)),
        }

## Form to assign doctor to a patient
class PatientAssignForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_user"].queryset = User.objects.filter(
            role=User.Role.DOCTOR
        )

    class Meta:
        model = PatientModel
        fields = ("assigned_user",)

## Form to edit consultation
class ConsultationEditForm(forms.ModelForm):
    class Meta:
        model = ConsultationModel
        exclude = ("patient",)
        widgets = {
            "datetime": forms.SelectDateWidget(
                years=range(now().year - 5, now().year + 20)
            ),
            "diagnosis": forms.Textarea(),
            "treatment": forms.Textarea(),
        }
        validators = {"datetime": MinValueValidator(now())}  # hmm doesn't seem to work

    def save(self, patient, commit=True):
        instance = super().save(False)
        instance.patient = patient
        if commit:
            instance.save()
        return instance

## Form to create new empty consultation
class ConsultationNewForm(forms.ModelForm):
    class Meta:
        model = ConsultationModel
        fields = ()

    def save(self, patient, commit=True):
        instance = super().save(False)
        instance.patient = patient
        if commit:
            instance.save()
        return instance

## Form to upload images
class ImageEditForm(forms.ModelForm):
    class Meta:
        model = ImageModel
        fields = ("image", "title")
        widgets = {}

    def save(self, patient, consultation, commit=True):
        instance = super().save(False)
        instance.patient = patient
        instance.consultation = consultation
        if commit:
            instance.save()
        return instance
