"""Admin registration for the ``conversations`` app."""
from django.contrib import admin

from . import models


class ConversationAdmin(admin.ModelAdmin):
    list_display = (
        # 'user_emails',
        # 'read_by_all',
    )
    raw_id_fields = ['users',
                     # 'archived_by',
                     # 'notified',
                     # 'unread_by'
    ]


class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'text')
    search_fields = ('text', )
    raw_id_fields = ['user', 'conversation']


# class BlockedUserAdmin(admin.ModelAdmin):
#     list_display = ('user', 'blocked_by', 'date')
#     raw_id_fields = ['user', 'blocked_by']


# admin.site.register(models.BlockedUser, BlockedUserAdmin)
admin.site.register(models.Conversation, ConversationAdmin)
admin.site.register(models.Message, MessageAdmin)
