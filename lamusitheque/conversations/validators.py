from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class FileSizeValidator(object):

    def __init__(self, max_size):
        self.max_size = max_size

    def __call__(self, value):
        filesize = value.size
        if filesize > self.max_size:
            raise ValidationError(
                "The maximum file size that can be uploaded is {}MB".format(self.max_size/(1024*1024))
            )
        else:
            return value

    def __eq__(self, other):
        return self.max_size == other.max_size
