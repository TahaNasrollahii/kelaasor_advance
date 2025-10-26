from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """دسترسی فقط برای ادمین‌ها"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsSupport(permissions.BasePermission):
    """دسترسی برای اعضای تیم پشتیبانی"""
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
    """دسترسی برای مدیران دوره‌ها و تخفیف‌ها"""
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
    """دسترسی برای مدرس‌ها به داده‌های خودشون"""
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
    """دسترسی ترکیبی برای ادمین و پشتیبانی"""
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
    """دسترسی ترکیبی برای ادمین و مدیر محصول"""
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or request.user.groups.filter(name__in=['ProductManager', 'Admin']).exists()
            )
        )