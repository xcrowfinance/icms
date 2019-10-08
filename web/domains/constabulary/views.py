# from web.domains.team.mixins import ContactsManagementMixin
from django.urls import reverse_lazy
from web.views import (ModelCreateView, ModelDetailView, ModelFilterView,
                       ModelUpdateView)

from .forms import ConstabulariesFilter, ConstabularyForm
from .models import Constabulary


class ConstabularyListView(ModelFilterView):
    template_name = 'web/constabulary/list.html'
    model = Constabulary
    filterset_class = ConstabulariesFilter

    class Display:
        fields = ['name', 'region_verbose', 'email']
        headers = ['Constabulary Name', 'Constabulary Region', 'Email Address']
        edit = True
        archive = True


class ConstabularyCreateView(ModelCreateView):
    template_name = 'web/constabulary/edit.html'
    form_class = ConstabularyForm
    model = Constabulary
    success_url = reverse_lazy('constabulary-list')


class ConstabularyEditView(ModelUpdateView):
    template_name = 'web/constabulary/edit.html'
    form_class = ConstabularyForm
    model = Constabulary
    success_url = reverse_lazy('constabulary-list')


class ConstabularyDetailView(ModelDetailView):
    form_class = ConstabularyForm
    model = Constabulary
