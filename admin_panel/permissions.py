from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Access restricted to admin users only."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsSupport(permissions.BasePermission):
    """Access for support team members."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.groups.filter(name='Support').exists()
                or request.user.is_superuser
            )
        )


class IsProductManager(permissions.BasePermission):
    """Access for course and discount managers."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.groups.filter(name='ProductManager').exists()
                or request.user.is_superuser
            )
        )


class IsInstructor(permissions.BasePermission):
    """Access for instructors to their own data."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.groups.filter(name='Instructor').exists()
                or request.user.is_superuser
            )
        )


class IsAdminOrSupport(permissions.BasePermission):
    """Combined access for admin and support roles."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(name__in=['Support', 'Admin']).exists()
            )
        )


class IsAdminOrProductManager(permissions.BasePermission):
    """Combined access for admin and product manager roles."""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(name__in=['ProductManager', 'Admin']).exists()
            )
        )