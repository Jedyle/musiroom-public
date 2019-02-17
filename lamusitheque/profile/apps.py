from django.apps import AppConfig
from django.apps import apps as django_apps


class AccountConfig(AppConfig):
    name = 'profile'
    label = 'profile'

    def ready(self):
        from actstream import registry
        registry.register(django_apps.get_model('auth.user'))
        registry.register(django_apps.get_model('django_comments_xtd.XtdComment'))
        registry.register(django_apps.get_model('pinax_badges.BadgeAward'))
