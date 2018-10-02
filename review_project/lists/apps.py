from django.apps import AppConfig

class ListsConfig(AppConfig):
    name = 'lists'

    def ready(self):
        from actstream import registry
        registry.register(self.get_model('ItemList'))
        registry.register(self.get_model('ListObject'))
