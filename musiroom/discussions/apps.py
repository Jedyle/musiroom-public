from django.apps import AppConfig
from importlib import import_module


class DiscussionsConfig(AppConfig):
    name = 'discussions'

    def ready(self):
        from actstream import registry
        import_module('discussions.handlers')
        registry.register(self.get_model('Discussion'))
