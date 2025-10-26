from django.contrib import admin
from .models import Ticket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 1
    readonly_fields = ['sender', 'created_at']
    can_delete = True
    show_change_link = True


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'user', 'status', 'department', 'is_public', 'created_at', 'updated_at']
    list_filter = ['status', 'department', 'is_public', 'created_at']
    search_fields = ['title', 'user__username', 'content']
    ordering = ['-created_at']
    inlines = [TicketReplyInline]


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'sender', 'created_at']
    list_filter = ['created_at']
    search_fields = ['ticket__title', 'sender__username', 'content']
    ordering = ['-created_at']
