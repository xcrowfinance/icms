from django import forms
from django_select2.forms import ModelSelect2Widget

from web.models import Country


class CertificateCheckForm(forms.Form):
    certificate_reference = forms.CharField(max_length=16)
    certificate_code = forms.CharField(max_length=16)
    country = forms.ModelChoiceField(
        queryset=Country.objects.all(),
        widget=ModelSelect2Widget(
            attrs={
                "data-minimum-input-length": 0,
                "data-placeholder": "-- Select Country",
            },
            search_fields=("name__icontains",),
        ),
    )
    organisation_name = forms.CharField(max_length=255)
