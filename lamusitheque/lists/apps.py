from importlib import import_module

from django.apps import AppConfig


class ListsConfig(AppConfig):
    name = 'lists'

    def ready(self):
        from actstream import registry
        import_module('lists.handlers')
        registry.register(self.get_model('ListObj'))
        registry.register(self.get_model('ListItem'))
