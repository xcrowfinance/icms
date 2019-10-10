from web.views import ModelFilterView

from .models import Template
from .forms import TemplatesFilter


class TemplateListView(ModelFilterView):
    template_name = 'web/template/list.html'
    model = Template
    filterset_class = TemplatesFilter
    page_title = 'Maintain Templates'
    permission_required = 'web.IMP_ADMIN:MAINTAIN_ALL:IMP_MAINTAIN_ALL'

    # Default display fields on the listing page of the model
    class Display:
        fields = [
            'template_name', 'application_domain_verbose',
            'template_type_verbose', 'template_status'
        ]
        headers = [
            'Template Name', 'Application Domain', 'Template Type',
            'Template Status'
        ]
        #  Display actions
        edit = True
        view = True
        archive = True
