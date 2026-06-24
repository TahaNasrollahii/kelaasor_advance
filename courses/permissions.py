from rest_framework import permissions
from purchase.models import Enrollment

class IsEnrolledOrVideoIsFree(permissions.BasePermission):
    """
    Allow access to a video if:
    - video.is_free == True
    OR
    - request.user is authenticated AND enrolled in the parent course (Enrollment exists and active)
    """

    def has_object_permission(self, request, view, obj):
        # obj expected to be a Video instance
        if getattr(obj, 'is_free', False):
            return True
        user = request.user
        if not user or not getattr(user, 'is_authenticated', False):
            return False

        # check Enrollment
        course = obj.chapter.course
        return Enrollment.objects.filter(user=user, course=course).exists()
