from django import forms
from django.utils.safestring import mark_safe
from django_select2 import forms as s2forms

from web.domains.case._import.forms import ChecklistBaseForm
from web.domains.case.forms import application_contacts
from web.domains.country.models import Country
from web.domains.firearms.models import ObsoleteCalibre
from web.domains.template.models import Template
from web.forms.widgets import DateInput

from . import models

TRUE_FALSE_CHOICES = (
    ("unknown", "---------"),
    (True, "Yes"),
    (False, "No"),
)


class PrepareSILForm(forms.ModelForm):
    additional_comments = forms.CharField(required=False, widget=forms.Textarea(attrs={"rows": 4}))

    class Meta:
        model = models.SILApplication
        fields = (
            "contact",
            "applicant_reference",
            "section1",
            "section2",
            "section5",
            "section58_obsolete",
            "section58_other",
            "other_description",
            "origin_country",
            "consignment_country",
            "military_police",
            "eu_single_market",
            "manufactured",
            "commodity_code",
            "know_bought_from",
            "additional_comments",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["contact"].queryset = application_contacts(self.instance)

        self.fields["origin_country"].queryset = Country.objects.filter(
            country_groups__name="Firearms and Ammunition (SIL) COOs", is_active=True
        )
        self.fields["consignment_country"].queryset = Country.objects.filter(
            country_groups__name="Firearms and Ammunition (SIL) COCs", is_active=True
        )

        self.fields["know_bought_from"].required = True
        self.fields["military_police"].required = True
        self.fields["eu_single_market"].required = True
        self.fields["manufactured"].required = True

        yes_no_fields = ["know_bought_from", "military_police", "eu_single_market", "manufactured"]
        for field in yes_no_fields:
            # The default label for unknown is "Unknown"
            self.fields[field].widget.choices = [
                ("unknown", "---------"),
                ("true", "Yes"),
                ("false", "No"),
            ]

    def clean(self):
        cleaned_data = super().clean()

        # At least one section should be selected
        licence_for = ["section1", "section2", "section5", "section58_obsolete", "section58_other"]
        sections = (cleaned_data.get(section) for section in licence_for)
        if not any(sections):
            self.add_error("section1", "You must select at least one 'section'")
            self.add_error("section2", "You must select at least one 'section'")
            self.add_error("section5", "You must select at least one 'section'")
            self.add_error("section58_obsolete", "You must select at least one 'section'")
            self.add_error("section58_other", "You must select at least one 'section'")

        if cleaned_data.get("section58_other") and not cleaned_data.get("other_description"):
            self.add_error("other_description", "You must enter this item")


class SILGoodsSection1Form(forms.ModelForm):
    class Meta:
        model = models.SILGoodsSection1
        fields = ("manufacture", "description", "quantity")
        widgets = {
            "manufacture": forms.Select(choices=TRUE_FALSE_CHOICES),
            "description": forms.Textarea({"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["manufacture"].required = True

    def clean_manufacture(self):
        manufactured_before_1900 = self.cleaned_data["manufacture"]
        if manufactured_before_1900:
            raise forms.ValidationError(
                "If your firearm was manufactured before 1900 then an import licence is not required."
            )

        return manufactured_before_1900


class SILGoodsSection2Form(forms.ModelForm):
    class Meta:
        model = models.SILGoodsSection2
        fields = ("manufacture", "description", "quantity")
        widgets = {
            "manufacture": forms.Select(choices=TRUE_FALSE_CHOICES),
            "description": forms.Textarea({"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["manufacture"].required = True

    def clean_manufacture(self):
        manufactured_before_1900 = self.cleaned_data["manufacture"]
        if manufactured_before_1900:
            raise forms.ValidationError(
                "If your firearm was manufactured before 1900 then an import licence is not required."
            )

        return manufactured_before_1900


class SILGoodsSection5Form(forms.ModelForm):
    SUBSECTION_CHOICES = (
        "5(1)(a) Any firearm capable of burst- or fully automatic fire and component parts of these.",
        "5(1)(ab) Any semi-automatic, self-loading or pump action rifled gun and carbines but not pistols.",
        (
            "5(1)(aba) Any firearm with a barrel less than 30 cm long or which is less than 60 cm long"
            " overall - short firearms (pistols and revolvers) and component parts of these."
        ),
        "5(1)(ac) Any pump-action or self-loading shotgun with a barrel less than 24 inches long or which is less than 40 inches long overall.",
        "5(1)(ad) Any smoothbore revolver gun except 9mm rim fire or muzzle loaded.",
        "5(1)(ae) Any rocket launcher or mortar which fires a stabilised missile other than for line throwing, pyrotechnics or signalling.",
        "5(1)(af) Any firearm using a self-contained gas cartridge system.",
        "5(1)(b) Any weapon designed or adapted to discharge noxious liquid, gas or other thing.",
        (
            "5(1)(c) Any cartridge with an explosive bullet or any ammo designed to discharge any noxious"
            " thing (as described above) and if capable of being used with a firearm of any description, any"
            " grenade, bomb or other like missile, rocket or shell designed to explode."
        ),
        "5(1A)(b) Explosive rockets or ammunition not covered in 5(1)(c)",
        "5(1A)(c) Any launcher or projector not covered in 5(1)(ae) designed to fire any rocket or ammunition covered by 5(1A)(b) or 5(1)(c).",
        "5(1A)(d) Incendiary ammunition.",
        "5(1A)(e) Armour-piercing ammunition.",
        "5(1A)(f) Expanding ammunition for use with pistols and revolvers.",
        "5(1A)(g)  Expanding, explosive, armour-piercing or incendiary projectiles.",
    )
    subsection = forms.ChoiceField(
        label="Section 5 subsection", choices=(), widget=s2forms.Select2Widget
    )

    class Meta:
        model = models.SILGoodsSection5
        fields = ("subsection", "manufacture", "description", "quantity", "unlimited_quantity")
        widgets = {
            "manufacture": forms.Select(choices=TRUE_FALSE_CHOICES),
            "description": forms.Textarea({"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["manufacture"].required = True

        self.fields["subsection"].choices = [("", "---------")] + [
            (x, x) for x in self.SUBSECTION_CHOICES
        ]

    def clean_manufacture(self):
        manufactured_before_1900 = self.cleaned_data["manufacture"]
        if manufactured_before_1900:
            raise forms.ValidationError(
                "If your firearm was manufactured before 1900 then an import licence is not required."
            )

        return manufactured_before_1900

    def clean(self):
        cleaned_data = super().clean()

        quantity = cleaned_data.get("quantity")
        unlimited_quantity = cleaned_data.get("unlimited_quantity")

        if not quantity and not unlimited_quantity:
            self.add_error(
                "quantity", "You must enter either a quantity or select unlimited quantity"
            )

        if unlimited_quantity:
            cleaned_data["quantity"] = None


class SILGoodsSection582ObsoleteForm(forms.ModelForm):
    obsolete_calibre = forms.ChoiceField(
        label="Obsolete Calibre", choices=(), widget=s2forms.Select2Widget
    )

    class Meta:
        model = models.SILGoodsSection582Obsolete
        fields = (
            "curiosity_ornament",
            "acknowledgment",
            "centrefire",
            "manufacture",
            "original_chambering",
            "obsolete_calibre",
            "description",
            "quantity",
        )
        widgets = {
            "curiosity_ornament": forms.Select(choices=TRUE_FALSE_CHOICES),
            "centrefire": forms.Select(choices=TRUE_FALSE_CHOICES),
            "manufacture": forms.Select(choices=TRUE_FALSE_CHOICES),
            "original_chambering": forms.Select(choices=TRUE_FALSE_CHOICES),
            "description": forms.Textarea({"rows": 3}),
            "obsolete_calibre": s2forms.Select2Widget,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curiosity_ornament"].required = True
        self.fields["centrefire"].required = True
        self.fields["manufacture"].required = True
        self.fields["original_chambering"].required = True

        calibres = ObsoleteCalibre.objects.filter(is_active=True).order_by("calibre_group", "name")

        self.fields["obsolete_calibre"].choices = [("", "---------")] + [
            (calibre.name, calibre.name) for calibre in calibres
        ]

    def clean_curiosity_ornament(self):
        curiosity_ornament = self.cleaned_data["curiosity_ornament"]
        if curiosity_ornament is False:
            raise forms.ValidationError(
                'If you do not intend to possess the firearm as a "curiosity or ornament" you'
                " cannot choose Section 58(2). You must change your selection to either"
                " Section 1, Section 2 or Section 5."
            )

        return curiosity_ornament

    def clean_acknowledgment(self):
        acknowledgment = self.cleaned_data["acknowledgment"]
        if not acknowledgment:
            raise forms.ValidationError("You must acknowledge the above statement")

        return acknowledgment

    def clean_manufacture(self):
        manufacture = self.cleaned_data["manufacture"]
        if manufacture is False:
            message = mark_safe(
                "If your firearm was manufactured after 1939 then you cannot choose Section 58(2)"
                " and must change your selection to either Section 1, Section 2 or Section 5."
                "<br/>If your firearm was manufactured before 1900 then an import licence is not"
                " required."
            )
            raise forms.ValidationError(message)

        return manufacture

    def clean_centrefire(self):
        centrefire = self.cleaned_data["centrefire"]
        if not centrefire:
            raise forms.ValidationError(
                "If your firearm is not a breech loading centrefire firearm, you cannot choose"
                " Section 58(2) - Obsolete Calibre. You must change your selection to either"
                " Section 1, Section 2 or Section 5."
            )

        return centrefire

    def clean_original_chambering(self):
        original_chambering = self.cleaned_data["original_chambering"]
        if not original_chambering:
            raise forms.ValidationError(
                "If your item does not retain its original chambering you cannot choose Obsolete Calibre."
            )

        return original_chambering


class SILGoodsSection582OtherForm(forms.ModelForm):
    class Meta:
        model = models.SILGoodsSection582Other
        fields = (
            "curiosity_ornament",
            "acknowledgment",
            "manufacture",
            "description",
            "quantity",
            "muzzle_loading",
            "rimfire",
            "rimfire_details",
            "ignition",
            "ignition_details",
            "ignition_other",
            "chamber",
            "bore",
            "bore_details",
        )
        widgets = {
            "curiosity_ornament": forms.Select(choices=TRUE_FALSE_CHOICES),
            "manufacture": forms.Select(choices=TRUE_FALSE_CHOICES),
            "muzzle_loading": forms.Select(choices=TRUE_FALSE_CHOICES),
            "rimfire": forms.Select(choices=TRUE_FALSE_CHOICES),
            "ignition": forms.Select(choices=TRUE_FALSE_CHOICES),
            "chamber": forms.Select(choices=TRUE_FALSE_CHOICES),
            "bore": forms.Select(choices=TRUE_FALSE_CHOICES),
            "description": forms.Textarea({"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["curiosity_ornament"].required = True
        self.fields["manufacture"].required = True
        self.fields["muzzle_loading"].required = True
        self.fields["rimfire"].required = True
        self.fields["ignition"].required = True
        self.fields["chamber"].required = True
        self.fields["bore"].required = True

    def clean_curiosity_ornament(self):
        curiosity_ornament = self.cleaned_data["curiosity_ornament"]
        if curiosity_ornament is False:
            raise forms.ValidationError(
                'If you do not intend to possess the firearm as a "curiosity or ornament" you'
                " cannot choose Section 58(2). You must change your selection to either"
                " Section 1, Section 2 or Section 5."
            )

        return curiosity_ornament

    def clean_acknowledgment(self):
        acknowledgment = self.cleaned_data["acknowledgment"]
        if not acknowledgment:
            raise forms.ValidationError("You must acknowledge the above statement")

        return acknowledgment

    def clean_manufacture(self):
        manufacture = self.cleaned_data["manufacture"]
        if manufacture is False:
            message = mark_safe(
                "If your firearm was manufactured after 1939 then you cannot choose Section 58(2)"
                " and must change your selection to either Section 1, Section 2 or Section 5."
                "<br/>If your firearm was manufactured before 1900 then an import licence is not"
                " required."
            )
            raise forms.ValidationError(message)

        return manufacture

    def clean(self):
        cleaned_data = super().clean()

        muzzle_loading = cleaned_data.get("muzzle_loading", False)
        rimfire = cleaned_data.get("rimfire", False)
        ignition = cleaned_data.get("ignition", False)
        chamber = cleaned_data.get("chamber", False)
        bore = cleaned_data.get("bore", False)

        last_questions = (muzzle_loading, rimfire, ignition, chamber, bore)
        if not any(last_questions):
            message = (
                "If your answer is 'No' to each of the previous five Yes/No questions, then you"
                " cannot choose 'Section 58(2) - Other'. You must change your selection to either"
                " Section 1, Section 2 or Section 5."
            )
            self.add_error("bore", message)

        if last_questions.count(True) > 1:
            self.add_error(
                "bore", "Only one of the above five questions can be answered with 'Yes'"
            )

        if rimfire and not cleaned_data.get("rimfire_details"):
            self.add_error("rimfire_details", "You must enter this item")

        ignition_details = cleaned_data.get("ignition_details")
        if ignition and not ignition_details:
            self.add_error("ignition_details", "You must enter this item")

        if (
            ignition
            and ignition_details == models.SILGoodsSection582Other.IgnitionDetail.OTHER
            and not cleaned_data.get("ignition_other")
        ):
            self.add_error("ignition_other", "You must enter this item")

        if bore and not cleaned_data.get("bore_details"):
            self.add_error("bore_details", "You must enter this item")


class SILChecklistForm(ChecklistBaseForm):
    class Meta:
        model = models.SILChecklist

        fields = (
            "authority_required",
            "authority_received",
            "authority_cover_items_listed",
            "quantities_within_authority_restrictions",
            "authority_police",
        ) + ChecklistBaseForm.Meta.fields


class SILChecklistOptionalForm(SILChecklistForm):
    """Used to enable partial saving of checklist."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for f in self.fields:
            self.fields[f].required = False


class ResponsePrepBaseForm(forms.ModelForm):
    """Base class form for editing description and quantity in the response preparation screen"""

    class Meta:
        fields = ("description", "quantity")


class ResponsePrepSILGoodsSection1Form(ResponsePrepBaseForm):
    class Meta:
        model = models.SILGoodsSection1
        fields = ResponsePrepBaseForm.Meta.fields


class ResponsePrepSILGoodsSection2Form(ResponsePrepBaseForm):
    class Meta:
        model = models.SILGoodsSection2
        fields = ResponsePrepBaseForm.Meta.fields


class ResponsePrepSILGoodsSection5Form(ResponsePrepBaseForm):
    class Meta:
        model = models.SILGoodsSection5
        fields = ResponsePrepBaseForm.Meta.fields + ("unlimited_quantity",)

    def clean(self):
        cleaned_data = super().clean()

        quantity = cleaned_data.get("quantity")
        unlimited_quantity = cleaned_data.get("unlimited_quantity")

        if not quantity and not unlimited_quantity:
            self.add_error(
                "quantity", "You must enter either a quantity or select unlimited quantity"
            )

        if unlimited_quantity:
            cleaned_data["quantity"] = None


class ResponsePrepSILGoodsSection582ObsoleteForm(ResponsePrepBaseForm):
    class Meta:
        model = models.SILGoodsSection582Obsolete
        fields = ResponsePrepBaseForm.Meta.fields


class ResponsePrepSILGoodsSection582OtherForm(ResponsePrepBaseForm):
    class Meta:
        model = models.SILGoodsSection582Other
        fields = ResponsePrepBaseForm.Meta.fields


class SILCoverLetterTemplateForm(forms.Form):
    template = forms.ModelChoiceField(queryset=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["template"].queryset = Template.objects.filter(
            template_code__startswith="COVER_FIREARMS_SEC5"
        )


class SILSupplementaryReportForm(forms.ModelForm):
    class Meta:
        model = models.SILSupplementaryReport
        fields = ("transport", "date_received", "bought_from")
        widgets = {"date_received": DateInput}

    def __init__(self, *args, application: models.SILApplication, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["bought_from"].queryset = application.importcontact_set.all()


class SILSupplementaryReportFirearmForm(forms.ModelForm):
    class Meta:
        model = models.SILSupplementaryReportFirearm
        fields = ("serial_number", "calibre", "model", "proofing")
