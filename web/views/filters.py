from web import models
from web.base.forms import widgets
from web.base.forms.forms import FilterSet
import django_filters as filter

_filter_config = {
    'label': {
        'cols': 'three',
        'optional_indicators': False
    },
    'input': {
        'cols': 'six'
    },
    'padding': {
        'right': 'three'
    },
    'actions': {
        'padding': {
            'left': 'three'
        },
        'submit': {
            'name': '',
            'value': '',
            'label': 'Search'
        }
    }
}


class TemplatesFilter(FilterSet):
    # Fields of the model that can be filtered
    template_name = filter.CharFilter(
        lookup_expr='icontains',
        widget=widgets.TextInput,
        help_text='Use % for wildcard searching.',
        label='Template Name')
    application_domain = filter.ChoiceFilter(
        choices=models.Template.DOMAINS,
        lookup_expr='exact',
        label='Adpplication Domain')
    template_type = filter.ChoiceFilter(
        choices=models.Template.TYPES,
        lookup_expr='exact',
        label='Template Type')

    class Meta:
        model = models.Template
        fields = []  # Django complains without fields set in the meta
        config = _filter_config


class OutboundEmailsFilter(FilterSet):
    # Fields of the model that can be filtered
    to_name = filter.CharFilter(
        lookup_expr='icontains', widget=widgets.TextInput, label='To Name')
    to_email = filter.CharFilter(
        lookup_expr='icontains', widget=widgets.TextInput, label='To Address')
    subject = filter.CharFilter(
        lookup_expr='icontains', widget=widgets.TextInput, label='Subject')
    sent_from = filter.DateFilter(
        field_name='last_requested_date',
        widget=widgets.DateInput,
        lookup_expr='gte',
        label='Sent From')
    to = filter.DateFilter(
        field_name='last_requested_date',
        widget=widgets.DateInput,
        lookup_expr='lte',
        label='To')
    status = filter.ChoiceFilter(
        choices=models.OutboundEmail.STATUSES,
        lookup_expr='icontains',
        label='Status')

    class Meta:
        model = models.OutboundEmail
        fields = []
        config = _filter_config


class TeamsFilter(FilterSet):
    name = filter.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=widgets.TextInput,
        label='Name')

    class Meta:
        model = models.Team
        fields = []
        config = _filter_config


class ConstabulariesFilter(FilterSet):
    name = filter.CharFilter(
        field_name='name',
        lookup_expr='icontains',
        widget=widgets.TextInput,
        label='Constabulary Name')

    region = filter.ChoiceFilter(
        field_name='region',
        choices=models.Constabulary.REGIONS,
        lookup_expr='icontains',
        widget=widgets.Select,
        label='Constabulary Region')

    email = filter.CharFilter(
        field_name='email',
        lookup_expr='icontains',
        widget=widgets.TextInput,
        label='Email Address')

    class Meta:
        model = models.Constabulary
        fields = []
        config = _filter_config


class CommoditiesFilter(FilterSet):
    commodity_code = filter.CharFilter(
        field_name='commotidy_code',
        lookup_expr='icontains',
        widget=widgets.TextInput,
        label='Commodity Code')

    commodity_type = filter.ChoiceFilter(
        field_name='type',
        choices=models.Commodity.TYPES,
        lookup_expr='icontains',
        widget=widgets.Select,
        label='Commodity Type')

    valid_start = filter.DateFilter(
        field_name='validity_start_date',
        widget=widgets.DateInput,
        lookup_expr='gte',
        label='Valid between')

    valid_end = filter.DateFilter(
        field_name='validity_end_date',
        widget=widgets.DateInput,
        lookup_expr='lte',
        label='and')

    is_archived = filter.BooleanFilter(
        field_name='is_active',
        widget=widgets.CheckboxInput,
        lookup_expr='exact',
        label='Search Archived')

    class Meta:
        model = models.Commodity
        fields = []
        config = _filter_config


class CommodityGroupsFilter(FilterSet):
    group_type = filter.ChoiceFilter(
        field_name='group_type',
        choices=models.CommodityGroup.TYPES,
        label='Group Type')
    commodity_types = filter.ChoiceFilter(
        field_name='commodity_type',
        choices=models.Commodity.TYPES,
        label='Commodity Types')

    group_code = filter.CharFilter(field_name='group_code', label='Group Code')
    group_name = filter.CharFilter(field_name='group_name', label='Group Name')

    is_archived = filter.BooleanFilter(
        field_name='is_active',
        widget=widgets.CheckboxInput,
        lookup_expr='exact',
        label='Search Archived')

    class Meta:
        models.CommodityGroup
        config = _filter_config
