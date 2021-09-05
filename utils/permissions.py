from typing import Union, List
from api.models.permissions import BasePermission, Administrator


def has_permissions(
    permissions: int, required: List[Union[int, BasePermission]]
) -> bool:
    """Returns `True` if this role has all provided permissions"""
    if permissions & Administrator().value:
        return True

    all_perms = 0
    for perm in required:
        if isinstance(perm, int):
            all_perms |= perm
        else:
            all_perms |= perm.value

    return permissions & all_perms == all_perms


def has_permission(permissions: int, permission: Union[BasePermission, int]) -> bool:
    """Returns `True` if this role has the provided permission"""
    if permissions & Administrator().value:
        return True

    if isinstance(permission, int):
        return permissions & permission == permission

    return permissions & permission.value == permission.value
