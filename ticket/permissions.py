from rest_framework import permissions

class IsTicketOwnerOrSupport(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if getattr(request.user, 'is_staff', False):
            return True
        return obj.user_id == request.user.id
