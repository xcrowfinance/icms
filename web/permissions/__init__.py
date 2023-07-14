from .perms import (
    ConstabularyObjectPermissions,
    ExporterObjectPermissions,
    ImporterObjectPermissions,
    PagePermissions,
    Perms,
    SysPerms,
)
from .service import (
    AppChecker,
    can_user_edit_firearm_authorities,
    can_user_edit_org,
    can_user_edit_section5_authorities,
    can_user_manage_org_contacts,
    can_user_view_org,
    can_user_view_search_cases,
    constabulary_add_contact,
    constabulary_get_contacts,
    constabulary_remove_contact,
    get_all_case_officers,
    get_case_officers_for_process_type,
    get_ilb_case_officers,
    get_org_obj_permissions,
    get_sanctions_case_officers,
    get_user_exporter_permissions,
    get_user_importer_permissions,
    get_users_with_permission,
    organisation_add_contact,
    organisation_get_contacts,
    organisation_remove_contact,
)
from .types import PermissionTextChoice

importer_object_permissions: list[tuple[str, str]] = Perms.obj.importer.get_permissions()
exporter_object_permissions: list[tuple[str, str]] = Perms.obj.exporter.get_permissions()
constabulary_object_permissions: list[tuple[str, str]] = Perms.obj.constabulary.get_permissions()
all_permissions: list[tuple[str, str]] = Perms.get_all_permissions()


__all__ = [
    "ConstabularyObjectPermissions",
    "ExporterObjectPermissions",
    "ImporterObjectPermissions",
    "PagePermissions",
    "Perms",
    "SysPerms",
    "AppChecker",
    "get_org_obj_permissions",
    "can_user_manage_org_contacts",
    "can_user_edit_firearm_authorities",
    "can_user_edit_org",
    "can_user_edit_section5_authorities",
    "can_user_view_org",
    "can_user_view_search_cases",
    "constabulary_add_contact",
    "constabulary_get_contacts",
    "constabulary_remove_contact",
    "get_all_case_officers",
    "get_ilb_case_officers",
    "get_sanctions_case_officers",
    "get_case_officers_for_process_type",
    "get_user_exporter_permissions",
    "get_user_importer_permissions",
    "get_users_with_permission",
    "organisation_add_contact",
    "organisation_get_contacts",
    "organisation_remove_contact",
    "PermissionTextChoice",
    "importer_object_permissions",
    "exporter_object_permissions",
    "constabulary_object_permissions",
    "all_permissions",
]
