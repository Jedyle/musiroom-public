from django.apps import AppConfig
from importlib import import_module


class CommentsConfig(AppConfig):
    name = 'comments'

    def ready(self):
        # wrapped into import_module to avoid deletion with pycharm
        import_module('comments.handlers')
