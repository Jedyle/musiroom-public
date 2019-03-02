from django.apps import AppConfig


class RatingsConfig(AppConfig):
    name = 'ratings'

    def ready(self):
        import ratings.handlers
        from actstream import registry
        registry.register(self.get_model('Review'))
