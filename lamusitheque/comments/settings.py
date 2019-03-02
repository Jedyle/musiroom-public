from django.conf import settings
from django.utils.module_loading import import_string

DEFAULT_MAX_DEPTH = 0
DEFAULT_ALLOWED_COMMENT_TARGETS = []


def get_max_depth():
    max_depth = getattr(settings, 'COMMENTS_MAX_DEPTH', DEFAULT_MAX_DEPTH)
    return max_depth


def get_allowed_comment_targets():
    allowed_comment_targets = [import_string(s) for s in
                               getattr(settings, 'COMMENTS_ALLOWED_COMMENT_TARGETS', DEFAULT_MAX_DEPTH)]
    return allowed_comment_targets
