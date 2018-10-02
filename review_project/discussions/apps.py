from django.apps import AppConfig


class DiscussionsConfig(AppConfig):
    name = 'discussions'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('Discussion'))
