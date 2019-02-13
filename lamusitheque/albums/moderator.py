from moderation import moderation
from moderation.moderator import GenericModerator

from .models import Genre


class GenreModerator(GenericModerator):
    notify_moderator = False
    notify_user = False


moderation.register(Genre, GenreModerator)  # Uses default moderation settingss
