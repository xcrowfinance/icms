from enum import StrEnum
from typing import TYPE_CHECKING, Any

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.forms.models import ModelForm
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.generic import FormView, UpdateView, View
from django.views.generic.detail import SingleObjectMixin
from django_filters import FilterSet
from django_filters.views import FilterView

from web.domains.case.export.views import (
    get_csf_schedule_legislation_config,
    get_show_schedule_statements_is_responsible_person,
)
from web.models import (
    CertificateApplicationTemplate,
    CertificateOfFreeSaleApplicationTemplate,
    CertificateOfGoodManufacturingPracticeApplicationTemplate,
    CertificateOfManufactureApplicationTemplate,
    CFSScheduleTemplate,
    ExportApplicationType,
    User,
)
from web.models.shared import AddressEntryType
from web.permissions import Perms
from web.types import AuthenticatedHttpRequest

from .forms import (
    CATFilter,
    CertificateOfFreeSaleApplicationTemplateForm,
    CertificateOfGoodManufacturingPracticeApplicationTemplateForm,
    CertificateOfManufactureApplicationTemplateForm,
    CFSManufacturerDetailsTemplateForm,
    CFSScheduleTemplateForm,
    CreateCATForm,
    EditCATForm,
)
from .utils import (
    get_user_templates,
    template_in_user_templates,
    user_can_edit_template,
)

if TYPE_CHECKING:
    from django.db import QuerySet


class CATListView(PermissionRequiredMixin, LoginRequiredMixin, FilterView):
    template_name = "web/domains/cat/list.html"
    context_object_name = "templates"
    filterset_class = CATFilter

    def has_permission(self) -> bool:
        return _has_permission(self.request.user)

    def get_queryset(self) -> "QuerySet[CertificateApplicationTemplate]":
        if self.request.GET.get("is_active") == "True":
            return get_user_templates(self.request.user)
        else:
            return get_user_templates(self.request.user, include_inactive=True)

    def get_context_data(self, **kwargs: dict[str, Any]) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Certificate Application Templates"

        return context

    def get_filterset_kwargs(self, filterset_class: FilterSet) -> dict[str, Any]:
        kwargs = super().get_filterset_kwargs(filterset_class)

        if not self.request.GET:
            # Default filter of "current" templates.
            kwargs["data"] = {"is_active": True}

        return kwargs


@login_required
def create(request: AuthenticatedHttpRequest) -> HttpResponse:
    with transaction.atomic():
        if not _has_permission(request.user):
            raise PermissionDenied

        if request.method == "POST":
            form = CreateCATForm(request.POST)
            if form.is_valid():
                cat: CertificateApplicationTemplate = form.save(commit=False)
                cat.owner = request.user
                cat.save()

                match cat.application_type:
                    case ExportApplicationType.Types.FREE_SALE:
                        template_cls = CertificateOfFreeSaleApplicationTemplate

                    case ExportApplicationType.Types.MANUFACTURE:
                        template_cls = CertificateOfManufactureApplicationTemplate

                    case ExportApplicationType.Types.GMP:
                        template_cls = CertificateOfGoodManufacturingPracticeApplicationTemplate

                template_cls.objects.create(template=cat)
                messages.success(request, f"Template '{cat.name}' created.")

                if cat.application_type == ExportApplicationType.Types.FREE_SALE:
                    cat.refresh_from_db()
                    cat.cfs_template.schedules.create()

                return redirect(reverse("cat:list"))
        else:
            form = CreateCATForm()

        context = {
            "page_title": "Create Certificate Application Template",
            "form": form,
            "read_only": False,
        }

        return render(request, "web/domains/cat/create.html", context)


def _has_permission(user: User) -> bool:
    exporter_admin = user.has_perm(Perms.sys.exporter_admin)
    exporter_user = user.has_perm(Perms.sys.exporter_access)

    return exporter_admin or exporter_user


class CatSteps(StrEnum):
    COM = "com"
    GMP = "gmp"
    CFS = "cfs"
    CFS_SCHEDULE = "cfs-schedule"


class CATEditView(PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "web/domains/cat/edit.html"
    read_only = False  # Determines editing or read-only behaviour.

    def has_permission(self) -> bool:
        return _has_permission(self.request.user)

    def test_func(self):
        """Runs before dispatch - Test template permission."""
        self.object = get_object_or_404(CertificateApplicationTemplate, pk=self.kwargs["cat_pk"])

        if not template_in_user_templates(self.request.user, self.object):
            return False

        # If read_only is true then we should be able to view the template as we've already
        # checked if the template is in the user templates.
        if self.read_only:
            return True

        return user_can_edit_template(self.request.user, self.object)

    def get_page_title(self):
        action = "View" if self.read_only else "Edit"
        page_title = f"{action} Certificate Application Template"

        return page_title

    def get_template_names(self) -> list[str]:
        match self.kwargs.get("step"):
            case CatSteps.CFS:
                template = "web/domains/cat/cfs/edit.html"
            case CatSteps.CFS_SCHEDULE:
                template = "web/domains/cat/cfs/edit-schedule.html"
            case _:
                template = "web/domains/cat/edit.html"

        return [template]

    def get_success_url(self):
        url_name = "view" if self.read_only else "edit"
        step = self.kwargs.get("step")
        step_pk = self.kwargs.get("step_pk")

        match step, step_pk:
            case None, _:
                return reverse(f"cat:{url_name}", kwargs={"cat_pk": self.object.pk})

            case step, None:
                return reverse(
                    f"cat:{url_name}-step", kwargs={"cat_pk": self.object.pk, "step": step}
                )

            case step, step_pk:
                return reverse(
                    f"cat:{url_name}-step-related",
                    kwargs={
                        "cat_pk": self.object.pk,
                        "step": step,
                        "step_pk": step_pk,
                    },
                )
            case _, _:
                return reverse("cat:list")

    def form_valid(self, form: ModelForm) -> HttpResponse:
        form.save()
        messages.success(self.request, f"Template '{self.object.name}' updated.")

        return super().form_valid(form)

    def get_form(self, form_class=None) -> ModelForm:
        form = super().get_form(form_class)

        if self.read_only:
            for fname in form.fields:
                form.fields[fname].disabled = True

        return form

    def get_form_class(self) -> type[ModelForm]:
        if "step" in self.kwargs:
            return form_class_for_application_type(
                self.object.application_type, self.kwargs["step"]
            )
        else:
            # This is the template's metadata form.
            return EditCATForm

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()

        if "step" in self.kwargs:
            step = self.kwargs["step"]
            match (self.object.application_type, step):
                case ExportApplicationType.Types.MANUFACTURE, CatSteps.COM:
                    instance = self.object.com_template

                case ExportApplicationType.Types.GMP, CatSteps.GMP:
                    instance = self.object.gmp_template

                case ExportApplicationType.Types.FREE_SALE, CatSteps.CFS:
                    instance = self.object.cfs_template

                case ExportApplicationType.Types.FREE_SALE, CatSteps.CFS_SCHEDULE:
                    instance = self.object.cfs_template.schedules.get(pk=self.kwargs["step_pk"])
                case _, _:
                    raise ValueError(f"Not supported: {self.object.application_type} {step}")
        else:
            instance = self.object

        kwargs["instance"] = instance

        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        app_type = self.object.application_type
        step = self.kwargs.get("step", "initial")
        form = context["form"]

        extra = {
            "page_title": self.get_page_title(),
            "application_type": self.object.application_type,
            "application_type_display": self.object.get_application_type_display(),
            "sidebar_links": self.get_sidebar_links(),
            "read_only": self.read_only,
            "step": step,
            "cat_pk": self.object.pk,
        }

        if app_type == ExportApplicationType.Types.FREE_SALE:
            if step == CatSteps.CFS:
                extra["schedules"] = self.object.cfs_template.schedules.all().order_by("created_at")

            if step == CatSteps.CFS_SCHEDULE:
                schedule = self.object.cfs_template.schedules.get(pk=self.kwargs["step_pk"])
                extra["schedule"] = schedule
                extra["process"] = self.object.cfs_template
                extra["legislation_config"] = get_csf_schedule_legislation_config()
                extra["show_schedule_statements_is_responsible_person"] = (
                    get_show_schedule_statements_is_responsible_person(schedule)
                )
                extra["edit_manufacturer_url"] = reverse(
                    "cat:cfs-manufacturer-update",
                    kwargs={"cat_pk": self.object.pk, "schedule_template_pk": schedule.pk},
                )
                extra["delete_manufacturer_url"] = reverse(
                    "cat:cfs-manufacturer-delete",
                    kwargs={"cat_pk": self.object.pk, "schedule_template_pk": schedule.pk},
                )

        if app_type == ExportApplicationType.Types.GMP and step == CatSteps.GMP:
            extra["include_contact"] = False
            extra["process"] = form.instance
            extra["country"] = "China"

        return context | extra

    def get_sidebar_links(self):
        type_ = self.object.application_type
        url_name = "view" if self.read_only else "edit"
        type_display = self.object.get_application_type_display()

        common_steps: list[tuple[str, str]] = [
            (reverse(f"cat:{url_name}", kwargs={"cat_pk": self.object.pk}), "Template"),
            (
                reverse(
                    f"cat:{url_name}-step", kwargs={"cat_pk": self.object.pk, "step": type_.lower()}
                ),
                f"{type_display} Application",
            ),
        ]

        match self.object.application_type:
            case ExportApplicationType.Types.FREE_SALE:
                app_specific: list[tuple[str, str]] = []

                template: CertificateOfFreeSaleApplicationTemplate = self.object.cfs_template
                for s_id, s in enumerate(template.schedules.all().order_by("id"), start=1):
                    app_specific.extend(self._get_schedule_links(s, s_id, url_name))

            case ExportApplicationType.Types.MANUFACTURE:
                app_specific = []
            case ExportApplicationType.Types.GMP:
                app_specific = []
            case _:
                app_specific = []

        return common_steps + app_specific

    def _get_schedule_links(
        self, schedule: CFSScheduleTemplate, num: int, url_name: str
    ) -> list[tuple[str, str]]:
        return [
            (
                reverse(
                    f"cat:{url_name}-step-related",
                    kwargs={
                        "cat_pk": self.object.pk,
                        "step": CatSteps.CFS_SCHEDULE,
                        "step_pk": schedule.pk,
                    },
                ),
                f"{url_name.title()} schedule {num}",
            ),
        ]


def form_class_for_application_type(type_code: str, step: str) -> type[ModelForm]:
    match type_code, step:
        case ExportApplicationType.Types.GMP, CatSteps.GMP:
            form_cls = CertificateOfGoodManufacturingPracticeApplicationTemplateForm

        case ExportApplicationType.Types.MANUFACTURE, CatSteps.COM:
            form_cls = CertificateOfManufactureApplicationTemplateForm

        case ExportApplicationType.Types.FREE_SALE, CatSteps.CFS:
            form_cls = CertificateOfFreeSaleApplicationTemplateForm

        case ExportApplicationType.Types.FREE_SALE, CatSteps.CFS_SCHEDULE:
            form_cls = CFSScheduleTemplateForm
        case _, _:
            raise ValueError(f"Type / Step not supported: {type_code} {step}")

    return form_cls


class CATReadOnlyView(CATEditView):
    read_only = True


class CATArchiveView(PermissionRequiredMixin, LoginRequiredMixin, View):
    def has_permission(self) -> bool:
        return _has_permission(self.request.user)

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs) -> HttpResponse:
        cat = get_object_or_404(CertificateApplicationTemplate, pk=kwargs["cat_pk"])

        user = self.request.user
        if not template_in_user_templates(user, cat) or not user_can_edit_template(user, cat):
            raise PermissionDenied

        cat.is_active = False
        cat.save()
        messages.success(self.request, f"Template '{cat.name}' archived.")

        return redirect("cat:list")


class CATRestoreView(PermissionRequiredMixin, LoginRequiredMixin, View):
    def has_permission(self) -> bool:
        return _has_permission(self.request.user)

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs) -> HttpResponse:
        cat = get_object_or_404(CertificateApplicationTemplate, pk=kwargs["cat_pk"])
        user = self.request.user
        if not template_in_user_templates(
            user, cat, include_inactive=True
        ) or not user_can_edit_template(user, cat):
            raise PermissionDenied

        cat.is_active = True
        cat.save()
        messages.success(self.request, f"Template '{cat.name}' restored.")

        return redirect("cat:list")


# Extra template views relating to the CFS Application.
class CFSTemplatePermissionRequiredMixin(PermissionRequiredMixin):
    """Permission required mixin common to all Edit CFS Template views."""

    def has_permission(self):
        if not _has_permission(self.request.user):
            return False

        cat = get_object_or_404(CertificateApplicationTemplate, pk=self.kwargs["cat_pk"])

        user = self.request.user
        if not template_in_user_templates(user, cat) or not user_can_edit_template(user, cat):
            return False

        return True


class CFSManufacturerUpdateView(LoginRequiredMixin, CFSTemplatePermissionRequiredMixin, UpdateView):
    pk_url_kwarg: str = "schedule_template_pk"
    form_class = CFSManufacturerDetailsTemplateForm
    template_name = "web/domains/cat/cfs/manufacturer-update.html"
    model = CFSScheduleTemplate

    def get_success_url(self):
        return reverse(
            "cat:edit-step-related",
            kwargs={
                "cat_pk": self.kwargs["cat_pk"],
                "step": CatSteps.CFS_SCHEDULE,
                "step_pk": self.object.pk,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context | {
            "page_title": "Edit Manufacturer",
            "previous_link": self.get_success_url(),
        }


class CFSManufacturerDeleteView(
    SingleObjectMixin, CFSTemplatePermissionRequiredMixin, LoginRequiredMixin, View
):
    # SingleObjectMixin
    model = CFSScheduleTemplate
    pk_url_kwarg: str = "schedule_template_pk"

    # View
    http_method_names = ["post"]

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs) -> HttpResponse:
        schedule = self.get_object()

        schedule.manufacturer_name = None
        schedule.manufacturer_address_entry_type = AddressEntryType.MANUAL
        schedule.manufacturer_postcode = None
        schedule.manufacturer_address = None
        schedule.save()

        return redirect(
            reverse(
                "cat:edit-step-related",
                kwargs={
                    "cat_pk": self.kwargs["cat_pk"],
                    "step": CatSteps.CFS_SCHEDULE,
                    "step_pk": schedule.pk,
                },
            )
        )


class CFSScheduleTemplateAddView(
    SingleObjectMixin, CFSTemplatePermissionRequiredMixin, LoginRequiredMixin, View
):
    # SingleObjectMixin
    model = CertificateApplicationTemplate
    pk_url_kwarg: str = "cat_pk"

    # View
    http_method_names = ["post"]

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs) -> HttpResponse:
        self.get_object().cfs_template.schedules.create()

        return redirect(
            reverse("cat:edit-step", kwargs={"cat_pk": self.kwargs["cat_pk"], "step": CatSteps.CFS})
        )


class CFSScheduleTemplateCopyView(
    SingleObjectMixin, CFSTemplatePermissionRequiredMixin, LoginRequiredMixin, View
):
    pk_url_kwarg: str = "schedule_template_pk"
    model = CFSScheduleTemplate

    # View
    http_method_names = ["post"]

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs) -> HttpResponse:
        schedule_template = self.get_object()

        copy_schedule(schedule_template, self.request.user)

        return redirect(
            reverse("cat:edit-step", kwargs={"cat_pk": self.kwargs["cat_pk"], "step": CatSteps.CFS})
        )


def copy_schedule(schedule: CFSScheduleTemplate, user: User) -> None:
    """Copy a template schedule.

    How to copy a model instance:
    https://docs.djangoproject.com/en/3.2/topics/db/queries/#copying-model-instances
    """

    # ManyToMany you can just use `.all()` to get the records
    # ForeignKeys you have to fetch from the db before the save.
    legislations_to_copy = schedule.legislations.all()
    products_to_copy = [p for p in schedule.products.all().order_by("pk")]

    schedule.pk = None
    schedule._state.adding = True
    schedule.created_by = user
    schedule.save()

    # Copy the legislation records
    schedule.legislations.set(legislations_to_copy)

    # copy the product records
    for product in products_to_copy:
        product_types_to_copy = [pt for pt in product.product_type_numbers.all().order_by("pk")]
        ingredients_to_copy = [i for i in product.active_ingredients.all().order_by("pk")]

        product.pk = None
        product._state.adding = True
        product.schedule = schedule
        product.save()

        for ptn in product_types_to_copy:
            ptn.pk = None
            ptn._state.adding = True
            ptn.product = product
            ptn.save()

        for ingredient in ingredients_to_copy:
            ingredient.pk = None
            ingredient._state.adding = True
            ingredient.product = product
            ingredient.save()


class CFSScheduleTemplateDeleteView(
    SingleObjectMixin, CFSTemplatePermissionRequiredMixin, LoginRequiredMixin, View
):
    pk_url_kwarg: str = "schedule_template_pk"
    model = CFSScheduleTemplate

    # View
    http_method_names = ["post"]

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs) -> HttpResponse:
        schedule_template = self.get_object()
        schedule_template.delete()

        return redirect(
            reverse("cat:edit-step", kwargs={"cat_pk": self.kwargs["cat_pk"], "step": CatSteps.CFS})
        )
