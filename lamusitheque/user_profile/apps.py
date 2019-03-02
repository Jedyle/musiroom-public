from django.apps import AppConfig
from django.apps import apps as django_apps
from importlib import import_module


class UserProfileConfig(AppConfig):
    name = 'user_profile'
    label = 'user_profile'

    def ready(self):
        from actstream import registry
        registry.register(django_apps.get_model('auth.user'))
        registry.register(django_apps.get_model('comments.comment'))
        registry.register(django_apps.get_model('pinax_badges.BadgeAward'))
        import_module('user_profile.handlers')
