from typing import Any

from django import forms
from django.utils import timezone
from django_select2.forms import ModelSelect2Widget
from guardian.shortcuts import get_objects_for_user

from web.forms.widgets import DateInput
from web.models import (
    EndorsementImportApplication,
    ImportApplication,
    ImportApplicationLicence,
    Importer,
    Office,
    Template,
    User,
)


class CreateImportApplicationForm(forms.Form):
    importer = forms.ModelChoiceField(
        queryset=Importer.objects.none(),
        label="Main Importer",
        widget=ModelSelect2Widget(
            attrs={
                "data-minimum-input-length": 0,
                "data-placeholder": "-- Select Importer",
            },
            search_fields=(
                "name__icontains",
                "user__first_name__icontains",
                "user__last_name__icontains",
            ),
        ),
    )
    importer_office = forms.ModelChoiceField(
        queryset=Office.objects.none(),
        label="Importer Office",
        widget=ModelSelect2Widget(
            attrs={
                "data-minimum-input-length": 0,
                "data-placeholder": "-- Select Office",
            },
            search_fields=(
                "postcode__icontains",
                "address_1__icontains",
                "address_2__icontains",
                "address_3__icontains",
                "address_4__icontains",
                "address_5__icontains",
                "address_6__icontains",
                "address_7__icontains",
                "address_8__icontains",
            ),
            dependent_fields={"importer": "importer"},
        ),
    )

    agent = forms.ModelChoiceField(
        required=False,
        queryset=Importer.objects.none(),
        label="Agent of Main Importer",
        widget=ModelSelect2Widget(
            attrs={
                "data-minimum-input-length": 0,
                "data-placeholder": "-- Select Agent",
            },
            search_fields=("main_importer__in", "importer"),
            # Key is a name of a field in a form.
            # Value is a name of a field in a model (used in `queryset`).
            dependent_fields={"importer": "main_importer"},
        ),
    )
    agent_office = forms.ModelChoiceField(
        required=False,
        queryset=Office.objects.none(),
        label="Agent Office",
        widget=ModelSelect2Widget(
            attrs={
                "data-minimum-input-length": 0,
                "data-placeholder": "-- Select Office",
            },
            search_fields=(
                "postcode__icontains",
                "address_1__icontains",
                "address_2__icontains",
                "address_3__icontains",
                "address_4__icontains",
                "address_5__icontains",
                "address_6__icontains",
                "address_7__icontains",
                "address_8__icontains",
            ),
            # Key is a name of a field in a form.
            # Value is a name of a field in a model (used in `queryset`).
            dependent_fields={"agent": "importer"},
        ),
    )

    def __init__(self, *args: Any, user: User, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.user = user

        active_importers = Importer.objects.filter(is_active=True, main_importer__isnull=True)
        importers = get_objects_for_user(
            user,
            ["web.is_contact_of_importer", "web.is_agent_of_importer"],
            active_importers,
            any_perm=True,
        )
        self.fields["importer"].queryset = importers
        self.fields["importer_office"].queryset = Office.objects.filter(
            is_active=True, importer__in=importers
        )

        active_agents = Importer.objects.filter(is_active=True, main_importer__in=importers)
        agents = get_objects_for_user(
            user,
            ["web.is_contact_of_importer"],
            active_agents,
        )
        self.fields["agent"].queryset = agents
        self.fields["agent_office"].queryset = Office.objects.filter(
            is_active=True, importer__in=agents
        )

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        importer = cleaned_data.get("importer")
        # if importer is not set agent and agent_office are not displayed.
        if not importer:
            return cleaned_data

        is_agent = self.user.has_perm("web.is_agent_of_importer", importer)
        if is_agent:
            if not cleaned_data.get("agent"):
                self.add_error("agent", "You must enter this item")

            if not cleaned_data.get("agent_office"):
                self.add_error("agent_office", "You must enter this item")

        return cleaned_data


class CreateWoodQuotaApplicationForm(CreateImportApplicationForm):
    """Create wood quota application form - Defines extra validation logic"""

    def clean(self) -> dict[str, Any]:
        cleaned_data = super().clean()

        if not self.has_error("importer_office"):
            office: Office = cleaned_data["importer_office"]
            postcode: str | None = office.postcode

            if not postcode or (not postcode.upper().startswith("BT")):
                self.add_error(
                    "importer_office",
                    "Wood applications can only be made for Northern Ireland traders.",
                )

        return cleaned_data


class CoverLetterForm(forms.ModelForm):
    class Meta:
        model = ImportApplication
        fields = ("cover_letter_text",)
        widgets = {"cover_letter_text": forms.Textarea(attrs={"lang": "html"})}

    def __init__(self, *args, readonly: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["cover_letter_text"].widget.attrs["readonly"] = readonly


class LicenceDateForm(forms.ModelForm):
    licence_start_date = forms.DateField(
        required=True, label="Licence Start Date", widget=DateInput
    )
    licence_end_date = forms.DateField(required=True, label="Licence End Date", widget=DateInput)

    class Meta:
        model = ImportApplicationLicence
        fields = ("licence_start_date", "licence_end_date")

    def clean(self):
        data = super().clean()
        start_date = data.get("licence_start_date")
        end_date = data.get("licence_end_date")
        if not start_date or not end_date:
            return
        today = timezone.now().date()

        if start_date < today:
            self.add_error("licence_start_date", "Date must be in the future.")

        if end_date < today:
            self.add_error("licence_end_date", "Date must be in the future.")

        if end_date <= start_date:
            self.add_error("licence_end_date", "End Date must be after Start Date.")


class LicenceDateAndPaperLicenceForm(LicenceDateForm):
    class Meta:
        model = ImportApplicationLicence
        fields = LicenceDateForm.Meta.fields + ("issue_paper_licence_only",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The default label for unknown is "Unknown"
        self.fields["issue_paper_licence_only"].required = True
        self.fields["issue_paper_licence_only"].widget.choices = [
            ("unknown", "Select One"),
            ("true", "Yes"),
            ("false", "No"),
        ]


class OPTLicenceForm(LicenceDateForm):
    reimport_period = forms.DecimalField(
        max_digits=9, decimal_places=2, min_value=0, label="Period for re-importation (months)"
    )

    class Meta:
        model = ImportApplicationLicence
        fields = LicenceDateForm.Meta.fields

    def save(self, commit=True):
        super().save(commit)

        opt_app = self.instance.import_application.get_specific_model()
        opt_app.reimport_period = self.cleaned_data["reimport_period"]
        opt_app.save()


class EndorsementChoiceImportApplicationForm(forms.ModelForm):
    content = forms.ModelChoiceField(
        queryset=Template.objects.filter(is_active=True, template_type=Template.ENDORSEMENT)
    )

    class Meta:
        model = EndorsementImportApplication
        fields = ("content",)

    def clean_content(self):
        endorsement = self.cleaned_data["content"]
        return endorsement.template_content


class EndorsementImportApplicationForm(forms.ModelForm):
    class Meta:
        model = EndorsementImportApplication
        fields = ("content",)


class ChecklistBaseForm(forms.ModelForm):
    class Meta:
        fields = (
            "case_update",
            "fir_required",
            "response_preparation",
            "validity_period_correct",
            "endorsements_listed",
            "authorisation",
        )

    def __init__(self, *args, readonly_form: bool = False, **kwargs):
        super().__init__(*args, **kwargs)

        # Change checklist fields to required (e.g. only selected is valid)
        for field in ["response_preparation", "authorisation"]:
            self.fields[field].required = True

        if readonly_form:
            for f in self.fields:
                self.fields[f].disabled = True
