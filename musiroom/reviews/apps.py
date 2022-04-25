from importlib import import_module

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    name = 'reviews'

    def ready(self):
        import_module('reviews.handlers')
        from actstream import registry
        registry.register(self.get_model('Review'))
