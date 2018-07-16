# Create your models here.

from django.db import models
from django.contrib.auth.models import User
from datetime import date
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.staticfiles.templatetags.staticfiles import static
import sys
from lists.models import ItemList

def get_100_last_years():
    lastyear = date.today().year
    return [str(i) for i in range(lastyear-1, lastyear-100, -1)]

def user_avatar_path(instance, filename):
    return 'avatars/user_{0}/{1}'.format(instance.user.id, filename)

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField("Avatar", null = True, blank = True, upload_to=user_avatar_path)
    birth = models.DateField("Date de naissance", null = True, blank = True)
    description = models.TextField("Description", max_length = 400, default = "", blank = True)

    SEX = [
        ("M","Homme"),
        ("F","Femme"),
        ("N","Anonyme"),
    ]

    sex = models.CharField("Sexe", max_length=1, default="N" , choices = SEX)
    display_birth = models.BooleanField("Afficher naissance", default = True)
    display_name = models.BooleanField("Afficher nom", default = False)
    display_sex = models.BooleanField("Afficher sexe", default = False)
    top_albums = models.ForeignKey(ItemList, on_delete=models.PROTECT)

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
            return static('account/images/profile.png')

    def save(self):
        if self.avatar:
            im = Image.open(self.avatar)
            output = BytesIO()
            #Resize/modify the image
            im.thumbnail((300,300))
            #after modifications, save it to the output
            im.save(output, format='JPEG', quality=90)
            output.seek(0)
            #change the imagefield value to be the newley modifed image value
            self.avatar = InMemoryUploadedFile(output,'ImageField', "%s.jpg" %self.avatar.name.split('.')[0], 'image/jpeg', sys.getsizeof(output), None)
        super(Account,self).save()
