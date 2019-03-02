from django.apps import AppConfig
from importlib import import_module


class AlbumsConfig(AppConfig):
    name = 'albums'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Artist'))
        registry.register(self.get_model('Album'))
        # import signals
        import_module('albums.handlers')

