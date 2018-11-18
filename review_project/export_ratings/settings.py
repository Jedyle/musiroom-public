from django.conf import settings

DEFAULT_EXPORT_TIMEDIFF = 0

def get_min_export_timediff():
    return getattr(settings, 'MIN_EXPORT_TIMEDIFF', DEFAULT_EXPORT_TIMEDIFF)
    
