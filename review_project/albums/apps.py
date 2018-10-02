from django.apps import AppConfig

class AlbumsConfig(AppConfig):
    name = 'albums'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Artist'))
        registry.register(self.get_model('Album'))
