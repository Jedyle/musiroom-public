from moderation import moderation
from moderation.db import ModeratedModel

from .models import Genre

moderation.register(Genre)  # Uses default moderation settingss
