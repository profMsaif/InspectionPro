from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsActiveUnblocked(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_active
            and not getattr(request.user, "is_blocked", False)
        )


class RoleBasedPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.is_active or getattr(request.user, "is_blocked", False):
            return False

        action_roles = getattr(view, "action_roles", {})
        action = getattr(view, "action", None)
        if action and action in action_roles:
            return request.user.role in action_roles[action] or request.user.is_superuser

        if request.method in SAFE_METHODS:
            allowed_roles = getattr(view, "read_roles", getattr(view, "allowed_roles", None))
        else:
            allowed_roles = getattr(view, "write_roles", getattr(view, "allowed_roles", None))

        if not allowed_roles:
            return True
        return request.user.role in allowed_roles or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        if not request.user.is_active or getattr(request.user, "is_blocked", False):
            return False
        return True
