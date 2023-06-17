import django_filters

from .models import PatientModel


class PatientFilter(django_filters.FilterSet):
    class Meta:
        model = PatientModel
        fields = [
            "firstName",
        ]  # "lastName", "gender", "dateofbirth"]
