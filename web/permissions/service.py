import dataclasses
from typing import TypeAlias

from django.contrib.auth.models import Group
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import QuerySet, Value
from guardian.shortcuts import (
    assign_perm,
    get_objects_for_user,
    get_user_perms,
    get_users_with_perms,
    remove_perm,
)

from web.models import (
    Exporter,
    ExporterUserObjectPermission,
    Importer,
    ImporterUserObjectPermission,
    User,
)
from web.permissions import ExporterObjectPermissions, ImporterObjectPermissions, Perms

ORGANISATION: TypeAlias = Importer | Exporter
IMP_OR_EXP_PERMS_T = type[ImporterObjectPermissions | ExporterObjectPermissions]


@dataclasses.dataclass(frozen=True)
class UserImporterPerms:
    user: User
    importer: Importer
    importer_perms: list[str]


@dataclasses.dataclass(frozen=True)
class UserExporterPerms:
    user: User
    exporter: Exporter
    exporter_perms: list[str]


def get_user_importer_permissions(user: User, importer: Importer) -> UserImporterPerms:
    iuo_perms = (
        ImporterUserObjectPermission.objects
        # Group by
        .values("user_id", "content_object_id")
        .filter(user=user, content_object=importer)
        # Field annotations
        .annotate(importer_perms=ArrayAgg("permission__codename", default=Value([])))
        .order_by("user_id", "content_object_id")
        .values_list("user_id", "content_object_id", "importer_perms", named=True)
    ).first()

    # Needed as the user may not have any perms for the supplied importer
    perms = iuo_perms.importer_perms if iuo_perms else []

    return UserImporterPerms(user, importer, perms)


def get_user_exporter_permissions(user: User, exporter: Exporter) -> UserExporterPerms:
    euo_perms = (
        ExporterUserObjectPermission.objects
        # Group by
        .values("user_id", "content_object_id")
        .filter(user=user, content_object=exporter)
        # Field annotations
        .annotate(exporter_perms=ArrayAgg("permission__codename", default=Value([])))
        .order_by("user_id", "content_object_id")
        .values_list("user_id", "content_object_id", "exporter_perms", named=True)
    ).first()

    # Needed as the user may not have any perms for the supplied exporter
    perms = euo_perms.exporter_perms if euo_perms else []

    return UserExporterPerms(user, exporter, perms)


def get_organisation_contacts(org: ORGANISATION) -> QuerySet[User]:
    """Current active contacts associated with importer, importer agent or exporter.

    An importer agent is still simply an importer.
    """

    obj_perms = _get_obj_permissions(org)

    # Remove the agent permission from both org permission lists.
    perms = [p.codename for p in obj_perms if p != obj_perms.is_agent]

    org_contacts: QuerySet[User] = get_users_with_perms(org, only_with_perms_in=perms)

    # Ensure they have org access
    org_contacts = filter_users_with_org_access(org, org_contacts)

    return org_contacts


def add_organisation_contact(org: ORGANISATION, user: User) -> None:
    obj_perms = _get_obj_permissions(org)

    for perm in [obj_perms.view, obj_perms.edit, obj_perms.is_contact]:
        assign_perm(perm, user, org)

    if org.is_agent():
        assign_perm(obj_perms.is_agent, user, org.get_main_org())

    add_group(user, obj_perms.get_group_name())


def remove_organisation_contact(org: ORGANISATION, user: User) -> None:
    for perm in get_user_perms(user, org):
        remove_perm(perm, user, org)

    obj_perms = _get_obj_permissions(org)

    if org.is_agent():
        remove_perm(obj_perms.is_agent, user, org.get_main_org())

    # Is the user linked to any other orgs
    other_orgs = get_objects_for_user(user, obj_perms.values, any_perm=True)

    if not other_orgs.exists():
        remove_group(user, obj_perms.get_group_name())


def can_manage_org_contacts(org: ORGANISATION, user: User) -> bool:
    obj_perms = _get_obj_permissions(org)

    is_ilb_admin = user.has_perm(Perms.sys.ilb_admin)
    can_manage = user.has_perm(obj_perms.manage_contacts_and_agents, org)

    return is_ilb_admin or can_manage


def _get_obj_permissions(org) -> IMP_OR_EXP_PERMS_T:
    match org:
        case Importer():
            return ImporterObjectPermissions
        case Exporter():
            return ExporterObjectPermissions
        case _:
            raise NotImplementedError(f"Unknown org {org}")


def add_group(user: User, group_name: str) -> None:
    group = Group.objects.get(name=group_name)
    user.groups.add(group)


def remove_group(user: User, group_name: str) -> None:
    group = Group.objects.get(name=group_name)
    user.groups.remove(group)


def filter_users_with_org_access(org: ORGANISATION, users: QuerySet[User]) -> QuerySet[User]:
    match org:
        case Importer():
            org_access = Perms.sys.importer_access.codename
        case Exporter():
            org_access = Perms.sys.exporter_access.codename
        case _:
            raise NotImplementedError(f"Unknown org {org}")

    # Note: We are ignoring user permissions by design
    return users.filter(groups__permissions__codename=org_access).distinct()
