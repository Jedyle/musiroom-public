from django.db.models.base import ModelBase
from django.core.exceptions import ImproperlyConfigured

class DiscussionAlreadyRegistered(Exception):
    pass

class DiscussionNotRegistered(Exception):
    pass

class DiscussionModelRegistration:
    def __init__(self):
        self._registry = []

    def register(self, model_or_iterable, admin_class=None, **options):
        """
        Register the given model(s).
        The model(s) should be Model classes, not instances.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model._meta.abstract:
                raise ImproperlyConfigured(
                    'The model %s is abstract, so it cannot be registered with admin.' % model.__name__
                )

            if model in self._registry:
                raise DiscussionAlreadyRegistered('The model %s is already registered' % model.__name__)

            # Ignore the registration if the model has been
            # swapped out.
            if not model._meta.swapped:
                # If we got **options then dynamically construct a subclass of
                # admin_class with those **options.
                if options:
                    # For reasons I don't quite understand, without a __module__
                    # the created class appears to "live" in the wrong place,
                    # which causes issues later on.
                    options['__module__'] = __name__

                # Instantiate the admin class to save in the registry
                self._registry.append(model)

    def unregister(self, model_or_iterable):
        """
        Unregister the given model(s).
        If a model isn't already registered, raise NotRegistered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise DiscussionNotRegistered('The model %s is not registered' % model.__name__)
            self._registry.remove(model)


discussions_registry = DiscussionModelRegistration()
