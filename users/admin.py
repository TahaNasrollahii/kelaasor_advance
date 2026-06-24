from django.contrib import admin
from django.utils.html import format_html
from .models import User, UserProfile, TeamEnrollment, TeamMember


# ---------- User ----------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("mobile", "full_name", "email", "is_active", "is_staff", "date_joined", "last_login")
    search_fields = ("mobile", "full_name", "email")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        ("User Information", {"fields": ("mobile", "full_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups")}),
        ("Timestamps", {"fields": ("date_joined", "last_login")}),
    )

# ---------- UserProfile ----------
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "city", "organization", "created_at", "updated_at")
    search_fields = ("user__mobile", "user__email", "city", "organization")
    list_filter = ("city",)
    autocomplete_fields = ["user"]


# ---------- TeamEnrollment ----------
@admin.register(TeamEnrollment)
class TeamEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("buyer", "course_slug", "reference_id", "created_at")
    search_fields = ("buyer__mobile", "buyer__full_name", "course_slug", "reference_id")
    autocomplete_fields = ["buyer"]


# ---------- TeamMember ----------
@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):

    list_display = ("team", "name", "mobile", "email", "user", "created_at")
    search_fields = ("name", "mobile", "email", "user__mobile", "user__full_name")
    autocomplete_fields = ["team", "user"]
