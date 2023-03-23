from typing import Any

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Q
from django_filters import CharFilter, ChoiceFilter, FilterSet
from guardian.forms import UserObjectPermissionsForm

from web.domains.importer.fields import PersonWidget
from web.errors import APIError
from web.models import Importer
from web.permissions import ImporterObjectPermissions, Perms
from web.utils.companieshouse import api_get_company


class ImporterIndividualForm(forms.ModelForm):
    class Meta:
        model = Importer
        fields = ["user", "eori_number", "region_origin", "comments"]
        widgets = {"user": PersonWidget}
        help_texts = {"eori_number": "EORI number should include the GBPR prefix"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["eori_number"].required = True

    def clean(self):
        """Set type as individual as Importer can be an organisation too."""
        self.instance.type = Importer.INDIVIDUAL
        return super().clean()

    def clean_eori_number(self):
        """Make sure eori number starts with GBPR."""
        eori_number = self.cleaned_data["eori_number"]
        prefix = "GBPR"
        if eori_number.startswith(prefix):
            return eori_number
        raise ValidationError(f"'{eori_number}' doesn't start with {prefix}")


class ImporterOrganisationForm(forms.ModelForm):
    class Meta:
        model = Importer
        fields = [
            "name",
            "registered_number",
            "eori_number",
            "region_origin",
            "comments",
        ]
        widgets = {"name": forms.Textarea(attrs={"rows": 1})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = True
        self.fields["registered_number"].required = True
        self.fields["eori_number"].required = True

    def clean(self):
        """Set type as organisation as Importer can be an individual too."""
        self.instance.type = Importer.ORGANISATION
        return super().clean()

    def clean_registered_number(self):
        registered_number = self.cleaned_data["registered_number"]

        # this is parsed in save()
        try:
            self.company = api_get_company(registered_number)
        except APIError as e:
            raise ValidationError(e.error_msg)

        if not self.company:
            raise ValidationError("Company is not present in Companies House records")

        return registered_number

    def clean_eori_number(self):
        """Make sure eori number starts with GB."""
        eori_number = self.cleaned_data["eori_number"]
        prefix = "GB"

        if eori_number.startswith(prefix):
            return eori_number

        raise ValidationError(f"'{eori_number}' doesn't start with {prefix}")

    def save(self, commit=True):
        instance = super().save(commit)

        if commit:
            office_address = self.company.get("registered_office_address", {})
            address_line_1 = office_address.get("address_line_1")
            address_line_2 = office_address.get("address_line_2")
            locality = office_address.get("locality")
            postcode = office_address.get("postal_code")

            if address_line_1 and postcode:
                instance.offices.get_or_create(
                    address_1=address_line_1,
                    postcode=postcode,
                    defaults={
                        "address_2": address_line_2,
                        "address_4": locality,
                    },
                )

        return instance


class ImporterFilter(FilterSet):
    importer_entity_type = ChoiceFilter(
        field_name="type", choices=Importer.TYPES, label="Importer Entity Type"
    )

    status = ChoiceFilter(
        field_name="is_active",
        choices=((True, "Current"), (False, "Archived")),
        lookup_expr="exact",
        label="Status",
    )

    name = CharFilter(lookup_expr="icontains", label="Importer Name", method="filter_importer_name")

    agent_name = CharFilter(lookup_expr="icontains", label="Agent Name", method="filter_agent_name")

    # Filter base queryset to only get importers that are not agents.
    @property
    def qs(self):
        return super().qs.filter(main_importer__isnull=True)

    def filter_importer_name(self, queryset, name, value):
        if not value:
            return queryset

        #  Filter organisation name for organisations and title, first_name, last_name
        #  for individual importers
        return queryset.filter(
            Q(name__icontains=value)
            | Q(user__title__icontains=value)
            | Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
        )

    def filter_agent_name(self, queryset, name, value):
        if not value:
            return queryset

        #  Filter agent name for organisations and title, first_name, last_name
        #  for individual importer agents
        return queryset.filter(
            Q(agents__name__icontains=value)
            | Q(agents__user__title__icontains=value)
            | Q(agents__user__first_name__icontains=value)
            | Q(agents__user__last_name__icontains=value)
        )

    class Meta:
        model = Importer
        fields: list[Any] = []


class AgentIndividualForm(forms.ModelForm):
    main_importer = forms.ModelChoiceField(
        queryset=Importer.objects.none(), label="Importer", disabled=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        importer = Importer.objects.filter(pk=self.initial["main_importer"])
        self.fields["main_importer"].queryset = importer
        self.fields["main_importer"].required = True
        self.fields["user"].required = True

    class Meta(ImporterIndividualForm.Meta):
        fields = ["main_importer", "user", "comments"]
        widgets = {"user": PersonWidget}

    def clean(self):
        self.instance.type = Importer.INDIVIDUAL
        return super().clean()


class AgentOrganisationForm(forms.ModelForm):
    main_importer = forms.ModelChoiceField(
        queryset=Importer.objects.none(), label="Importer", disabled=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        importer = Importer.objects.filter(pk=self.initial["main_importer"])
        self.fields["main_importer"].queryset = importer
        self.fields["main_importer"].required = True
        self.fields["name"].required = True
        self.fields["registered_number"].required = True

    class Meta(ImporterOrganisationForm.Meta):
        fields = [
            "main_importer",
            "name",
            "registered_number",
            "comments",
        ]

        widgets = {"name": forms.Textarea(attrs={"rows": 1})}

    def clean(self):
        self.instance.type = Importer.ORGANISATION
        return super().clean()


# Needed for now because we don't want to show all permissions (everything but the agent)
def get_importer_object_permissions(
    importer: Importer,
) -> list[tuple[ImporterObjectPermissions, str]]:
    """Return object permissions for the Importer model with a label for each."""

    object_permissions = [
        (Perms.obj.importer.view, "View Applications / Licences"),
        (Perms.obj.importer.edit, "Edit Applications / Vary Licences"),
        (Perms.obj.importer.is_contact, "Is Importer Contact"),
    ]

    # The agent should never have the manage_contacts_and_agents permission.
    if not importer.is_agent():
        object_permissions.append(
            (Perms.obj.importer.manage_contacts_and_agents, "Approve / Reject Agents and Importers")
        )

    return object_permissions


class ImporterUserObjectPermissionsForm(UserObjectPermissionsForm):
    obj: Importer

    def get_obj_perms_field_widget(self):
        return forms.CheckboxSelectMultiple(attrs={"class": "radio-relative"})

    def get_obj_perms_field_choices(self):
        # Only iterate over permissions we show in the main edit importer view
        return [(p.codename, label) for (p, label) in get_importer_object_permissions(self.obj)]
