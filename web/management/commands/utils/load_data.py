from django.core.management import call_command

from .add_application_type_data import (
    add_export_application_type_data,
    add_import_application_type_data,
    add_import_application_type_endorsements,
)
from .add_commodity_group_usage_data import add_usage_data
from .add_constabulary_data import add_constabulary_data
from .add_email_template_data import add_email_gov_notify_templates
from .add_fa_data import add_firearms_act_data, add_obsolete_calibre_data
from .add_sanction_data import add_sanction_data
from .add_template_data import (
    add_cfs_declaration_templates,
    add_cfs_schedule_data,
    add_declaration_templates,
    add_email_templates,
    add_endorsement_templates,
    add_letter_fragment_templates,
    add_letter_templates,
    add_schedule_translation_templates,
    add_user_management_email_templates,
)


def load_app_test_data():
    call_command("set_icms_sites")
    call_command("loaddata", "overseas_regions")
    call_command("loaddata", "country")
    call_command("loaddata", "country_groups")
    call_command("loaddata", "country_translation_set")
    call_command("loaddata", "country_translation")
    add_cfs_schedule_data()
    add_cfs_declaration_templates()
    add_schedule_translation_templates()
    add_declaration_templates()
    add_endorsement_templates()
    add_email_templates()
    add_letter_templates()
    add_letter_fragment_templates()
    add_user_management_email_templates()
    add_export_application_type_data()
    add_import_application_type_data()
    add_import_application_type_endorsements()
    call_command("loaddata", "units")
    call_command("loaddata", "commodity_types")
    call_command("loaddata", "commodities")
    call_command("loaddata", "commodity_groups")
    add_usage_data()
    add_constabulary_data()
    add_firearms_act_data()
    add_obsolete_calibre_data()
    call_command("loaddata", "product_legislations")
    add_sanction_data()
    add_email_gov_notify_templates()
