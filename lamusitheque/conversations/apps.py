from importlib import import_module

from django.apps import AppConfig


class ConversationConfig(AppConfig):
    name = 'conversations'
    verbose_name = "Conversations"

    def ready(self):
        import_module('conversations.handlers')
