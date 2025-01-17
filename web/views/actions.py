from typing import Any

from django.contrib import messages
from django.core.exceptions import SuspiciousOperation
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.safestring import mark_safe

from web.models import (
    Commodity,
    CommodityGroup,
    Constabulary,
    CountryTranslationSet,
    Exporter,
    File,
    FirearmsAct,
    Importer,
    ObsoleteCalibre,
    ObsoleteCalibreGroup,
    ProductLegislation,
    SanctionEmail,
    Section5Clause,
    Template,
)

# Classes that previously inherited from Archivable.
ARCHIVABLE_MODEL = (
    Commodity,
    CommodityGroup,
    Constabulary,
    CountryTranslationSet,
    Exporter,
    File,
    FirearmsAct,
    Importer,
    ObsoleteCalibre,
    ObsoleteCalibreGroup,
    ProductLegislation,
    SanctionEmail,
    Section5Clause,
    Template,
)


class ListAction:
    def __init__(self, inline=False, icon_only=False):
        self.inline = inline
        self.icon_only = icon_only

    def _get_item(self, request, model):
        _id = request.POST.get("item")
        return get_object_or_404(model, pk=_id)

    def display(self, object):
        return True


class PostAction(ListAction):
    template = "model/actions/submit.html"
    template_inline = "model/actions/submit-inline.html"

    # Overridden in child classes
    action = "unset"
    label = "unset"

    confirm = True  # confirm action before submitting

    def as_html(self, object, csrf_token, **kwargs):
        return mark_safe(
            render_to_string(
                self.template_inline if self.inline else self.template,
                self.get_context_data(object, csrf_token, **kwargs),
            )
        )

    def get_context_data(self, obj, csrf_token, **kwargs):
        return {
            "icon": getattr(self, "icon", None),
            "csrf_token": csrf_token,
            "object": obj,
            "confirm": self.confirm,
            "confirm_message": getattr(self, "confirm_message", None),
            "action": self.action,
            "label": self.label,
            "icon_only": self.icon_only,
        }

    def handle(self, request, view, *args, **kwargs):
        raise SuspiciousOperation("Not implemented!")


class LinkAction(ListAction):
    template = "model/actions/link.html"
    template_inline = "model/actions/link-inline.html"

    # Overridden in child classes
    icon = "unset"
    label = "unset"

    def href(self, object):
        return f"{object.id}/"

    def as_html(self, object, *args, **kwargs):
        return mark_safe(
            render_to_string(
                self.template_inline if self.inline else self.template,
                self.get_context_data(object),
            )
        )

    def get_context_data(self, object):
        return {
            "icon": self.icon or None,
            "object": object,
            "label": self.label,
            "href": self.href(object),
            "icon_only": self.icon_only,
        }


# note that this seems to be unused, and web/templates/tables/tables.html (lines
# 27-28) hardcodes the view-link generation
class View(LinkAction):
    label = "View"
    icon = "icon-eye"


class ViewObject(LinkAction):
    label = "View"
    icon = "icon-eye"

    def href(self, obj):
        return obj.get_absolute_url()


class Edit(LinkAction):
    label = "Edit"
    icon = "icon-pencil"

    def __init__(self, *args: Any, hide_if_archived_object: bool = False, **kwargs: Any) -> None:
        self.hide_if_archived_object = hide_if_archived_object
        super().__init__(*args, **kwargs)

    def href(self, object):
        return f"{object.id}/edit/"

    def display(self, object):
        if (
            # The logic was previously if isinstance(object, Archivable)
            isinstance(object, ARCHIVABLE_MODEL)
            and self.hide_if_archived_object
            and not object.is_active
        ):
            return False
        return True


class EditTemplate(Edit):
    label = "Edit"
    icon = "icon-pencil"

    def href(self, instance: Template) -> str:
        if instance.template_type == Template.CFS_DECLARATION_TRANSLATION:
            return reverse("template-cfs-declaration-translation-edit", kwargs={"pk": instance.pk})
        elif instance.template_type == Template.CFS_SCHEDULE_TRANSLATION:
            return reverse("template-cfs-schedule-translation-edit", kwargs={"pk": instance.pk})

        return f"{instance.id}/edit/"

    def display(self, object: Template) -> bool:
        # CFS Schedule defines the reference text in English, and it should not be editable
        if object.template_type == Template.CFS_SCHEDULE:
            return False
        return super().display(object)


class Archive(PostAction):
    action = "archive"
    label = "Archive"
    confirm_message = "Are you sure you want to archive this record?"
    icon = "icon-bin"

    def display(self, object):
        # The logic was previously if isinstance(object, Archivable)
        return isinstance(object, ARCHIVABLE_MODEL) and object.is_active

    def handle(self, request, view):
        model = self._get_item(request, view.model)
        model.is_active = False
        model.save()

        messages.success(request, "Record archived successfully")


class ArchiveTemplate(Archive):

    def display(self, template: Template) -> bool:
        if template.template_type == Template.EMAIL_TEMPLATE:
            return False
        return super().display(template)


class Unarchive(PostAction):
    action = "unarchive"
    label = "Unarchive"
    confirm_message = "Are you sure you want to unarchive this record?"
    icon = "icon-undo2"

    def display(self, object):
        # The logic was previously if isinstance(object, Archivable)
        return isinstance(object, ARCHIVABLE_MODEL) and not object.is_active

    def handle(self, request, view):
        model = self._get_item(request, view.model)
        model.is_active = True
        model.save()

        messages.success(request, "Record restored successfully")


class UnarchiveTemplate(Unarchive):

    def display(self, template: Template) -> bool:
        if template.template_type == Template.EMAIL_TEMPLATE:
            return False
        return super().display(template)


class CreateIndividualAgent(LinkAction):
    label = "Create Individual Agent"
    icon = "icon-user-plus"

    def href(self, object):
        return reverse(
            "importer-agent-create", kwargs={"importer_pk": object.pk, "entity_type": "individual"}
        )


class CreateOrganisationAgent(LinkAction):
    label = "Create Organisation Agent"
    icon = "icon-user-plus"

    def href(self, object):
        return reverse(
            "importer-agent-create",
            kwargs={"importer_pk": object.pk, "entity_type": "organisation"},
        )


class CreateExporterAgent(LinkAction):
    label = "Create Agent"
    icon = "icon-user-plus"

    def href(self, object):
        return reverse("exporter-agent-create", kwargs={"exporter_pk": object.pk})
