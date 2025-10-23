from django.contrib import admin
from django.utils.html import format_html
from .models import User, UserProfile, OTP, TeamEnrollment, TeamMember


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'full_name', 'is_active', 'is_staff', 'created_at')
    search_fields = ('mobile', 'full_name')
    list_filter = ('is_active', 'is_staff')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('اطلاعات کاربری', {'fields': ('mobile', 'full_name', 'email')}),
        ('دسترسی‌ها', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups')}),
        ('زمان‌ها', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'city', 'country')
    search_fields = ('user__mobile', 'first_name', 'last_name', 'city', 'country')
    list_filter = ('country',)
    autocomplete_fields = ['user']


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('mobile', 'code', 'is_used', 'is_expired_display', 'created_at')
    search_fields = ('mobile', 'code')
    list_filter = ('is_used',)
    ordering = ('-created_at',)
    readonly_fields = ('mobile', 'code', 'created_at')

    def is_expired_display(self, obj):
        color = "red" if obj.is_expired else "green"
        text = "Expired" if obj.is_expired else "Valid"
        return format_html(f'<b style="color:{color}">{text}</b>')
    is_expired_display.short_description = "Expiration Status"


@admin.register(TeamEnrollment)
class TeamEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('owner', 'course', 'created_at')
    search_fields = ('owner__mobile', 'course__title')
    autocomplete_fields = ['owner', 'course']


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'full_name', 'mobile')
    search_fields = ('full_name', 'mobile')
    autocomplete_fields = ['enrollment']
