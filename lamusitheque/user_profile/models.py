import sys
from datetime import date
from io import BytesIO

from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from pinax.badges.models import BadgeAward

from lists.models import ListObj
from .badges import *


@property
def api_lookup_value(self):
    return self.username


User.add_to_class("api_lookup_value", api_lookup_value)


def get_100_last_years():
    lastyear = date.today().year
    return [str(i) for i in range(lastyear - 1, lastyear - 100, -1)]


def user_avatar_path(instance, filename):
    return 'avatars/user_{0}/{1}'.format(instance.user.id, filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField("Avatar", null=True, blank=True, upload_to=user_avatar_path)
    birth = models.DateField("Birth date", null=True, blank=True)
    description = models.TextField("Description", max_length=400, default="", blank=True)

    SEX = [
        ("M", "Male"),
        ("F", "Female"),
        ("N", "Anonymous"),
    ]

    sex = models.CharField("Sex", max_length=1, default="N", choices=SEX)
    display_birth = models.BooleanField("Display birth", default=False)
    display_name = models.BooleanField("Display name", default=False)
    display_sex = models.BooleanField("Display gender", default=False)
    top_albums = models.ForeignKey(ListObj, blank=True, null=True, on_delete=models.PROTECT)

    last_activity = models.DateTimeField('Last activity', auto_now_add=True)

    def __init__(self, *args, **kwargs):
        super(Profile, self).__init__(*args, **kwargs)
        self.__old_avatar = self.avatar

    def __str__(self):
        return self.user.username

    def get_age(self):
        born = self.birth
        today = date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def get_avatar(self):
        if self.avatar:
            return self.avatar.url
        else:
            return static('user_profile/images/user_profile.png')

    @property
    def api_lookup_value(self):
        return self.user.username

    def get_absolute_url(self):
        return self.user.get_absolute_url()

    def save(self):

        # do this only if avatar has changed
        if self.avatar != self.__old_avatar:
            im = Image.open(self.avatar)
            output = BytesIO()
            im = im.convert('RGB')
            im.thumbnail((300, 300))
            im.save(output, format='JPEG', quality=90)
            output.seek(0)
            self.avatar = InMemoryUploadedFile(output, 'ImageField', "%s.jpg" % self.avatar.name.split('.')[0],
                                               'image/jpeg', sys.getsizeof(output), None)
        super(Profile, self).save()


# Monkey patch Pinax BadgeAward's __str__ method to display badges in activity.

def badge_to_string(self):
    return self.name


BadgeAward.add_to_class('__str__', badge_to_string)
