from django.apps import AppConfig

class FriendshipConfig(AppConfig):
    name = 'friendship'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Follow'))
