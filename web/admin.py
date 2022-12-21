from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from web.domains.case._import.models import ImportApplication, ImportApplicationType
from web.domains.case._import.sanctions.models import SanctionsAndAdhocApplication
from web.domains.case.export.models import (
    ExportApplication,
    ExportApplicationType,
    Exporter,
)
from web.domains.country.models import Country, CountryGroup
from web.flow.models import Process, Task

from .models import (
    Commodity,
    CommodityGroup,
    CommodityType,
    DerogationsApplication,
    Importer,
    PersonalEmail,
    PhoneNumber,
    SanctionsAndAdhocApplicationGoods,
    Template,
    User,
)


class CountryGroupModelForm(forms.ModelForm):
    comments = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = CountryGroup
        fields = ["name", "comments", "countries"]


class CountryGroupAdmin(admin.ModelAdmin):
    form = CountryGroupModelForm


admin.site.register(User, UserAdmin)
admin.site.register(CommodityType)
admin.site.register(Commodity)
admin.site.register(CommodityGroup)
admin.site.register(Template)
admin.site.register(Task)
admin.site.register(ContentType)
admin.site.register(Process)
admin.site.register(PhoneNumber)
admin.site.register(PersonalEmail)
admin.site.register(Importer)
admin.site.register(ImportApplicationType)
admin.site.register(ExportApplicationType)
admin.site.register(CountryGroup, CountryGroupAdmin)
admin.site.register(Country)
admin.site.register(ImportApplication)
admin.site.register(ExportApplication)
admin.site.register(Exporter)
admin.site.register(SanctionsAndAdhocApplication)
admin.site.register(SanctionsAndAdhocApplicationGoods)
admin.site.register(DerogationsApplication)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs: QuerySet[Permission] = super().get_queryset(request)

        qs = _filter_icms_permissions(qs)
        qs = qs.select_related("content_type").order_by("content_type__model")

        return qs


# Group already gets registered to improve performance of fetching system permissions
# Therefore unregister before adding GroupAdmin below
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """Copied from django.contrib.auth.admin.GroupAdmin"""

    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("permissions",)

    def formfield_for_manytomany(self, db_field, request=None, **kwargs):
        if db_field.name == "permissions":
            qs: QuerySet[Permission] = kwargs.get("queryset", db_field.remote_field.model.objects)

            qs = _filter_icms_permissions(qs)

            # Avoid a major performance hit resolving permission names which
            # triggers a content_type load:
            kwargs["queryset"] = qs.select_related("content_type")

        return super().formfield_for_manytomany(db_field, request=request, **kwargs)


def _filter_icms_permissions(qs: QuerySet[Permission]) -> QuerySet[Permission]:
    return qs.filter(
        content_type__app_label="web",
        content_type__model__in=[
            # System-wide global permissions
            "globalpermission",
            # Models with object level permissions
            "importer",
            "exporter",
        ],
    )
