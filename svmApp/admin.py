from django.contrib import admin

# Register your models here.
from .models import PatientModel


@admin.register(PatientModel)
class PatientAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        "slug": (
            "firstName",
            "lastName",
        )
    }
