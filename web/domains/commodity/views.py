from django.urls import reverse_lazy
from web.views import (ModelCreateView, ModelDetailView, ModelFilterView,
                       ModelUpdateView)
from web.views.actions import Archive, Edit, Unarchive

from .forms import (CommodityEditForm, CommodityFilter, CommodityForm,
                    CommodityGroupEditForm, CommodityGroupFilter,
                    CommodityGroupForm)
from .models import Commodity, CommodityGroup

permissions = 'web.IMP_ADMIN:MAINTAIN_ALL:IMP_MAINTAIN_ALL'


class CommodityListView(ModelFilterView):
    template_name = 'web/commodity/list.html'
    filterset_class = CommodityFilter
    model = Commodity
    permission_required = permissions

    class Display:
        fields = [
            'commodity_code', ('validity_start_date', 'validity_end_date')
        ]
        fields_config = {
            'commodity_code': {
                'header': 'Commodity Code',
                'link': True
            },
            'validity_start_date': {
                'header': 'Validity Start Date'
            },
            'validity_end_date': {
                'header': 'Validity End Date'
            }
        }
        actions = [Archive(), Unarchive(), Edit()]


class CommodityEditView(ModelUpdateView):
    template_name = 'web/commodity/edit.html'
    form_class = CommodityEditForm
    model = Commodity
    success_url = reverse_lazy('commodity-list')
    permission_required = permissions


class CommodityCreateView(ModelCreateView):
    template_name = 'web/commodity/create.html'
    form_class = CommodityForm
    success_url = reverse_lazy('commodity-list')
    permission_required = permissions


class CommodityDetailView(ModelDetailView):
    form_class = CommodityForm
    model = Commodity
    permission_required = permissions


class CommodityGroupListView(ModelFilterView):
    template_name = 'web/commodity-group/list.html'
    filterset_class = CommodityGroupFilter
    model = CommodityGroup
    permission_required = permissions

    class Display:
        fields = [
            'group_type_verbose', 'commodity_type_verbose',
            ('group_code', 'group_name'), 'group_description'
        ]
        fields_config = {
            'group_type_verbose': {
                'header': 'Group Type'
            },
            'commodity_type_verbose': {
                'header': 'Commodity Type'
            },
            'group_code': {
                'header': 'Group Code'
            },
            'group_name': {
                'header': 'Group Name'
            },
            'group_description': {
                'header': 'Description'
            }
        }
        actions = [Archive(), Unarchive(), Edit()]


class CommodityGroupEditView(ModelUpdateView):
    template_name = 'web/commodity-group/edit.html'
    form_class = CommodityGroupEditForm
    model = CommodityGroup
    success_url = reverse_lazy('commodity-group-list')
    permission_required = permissions


class CommodityGroupCreateView(ModelCreateView):
    template_name = 'web/commodity-group/edit.html'
    form_class = CommodityGroupForm
    model = CommodityGroup
    success_url = reverse_lazy('commodity-group-list')
    permission_required = permissions


class CommodityGroupDetailView(ModelDetailView):
    form_class = CommodityGroupForm
    model = CommodityGroup
    permission_required = permissions