from django.conf import settings

DEFAULT_SEARCH_FIELD = 'name'


def get_search_config():
    return getattr(settings, 'AUTOCOMPLETE_SEARCH_FIELDS', {})
