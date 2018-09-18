from django.conf import settings

DEFAULT_SEARCH_FIELD = 'name'

def get_search_fields_config():
    return getattr(settings, 'DISCUSSIONS_SEARCH_FIELDS', {})
