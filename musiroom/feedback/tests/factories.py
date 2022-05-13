import factory
import factory.fuzzy
from django.conf import settings

from user_profile.tests.factories import UserFactory


class FeedbackFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "feedback.Feedback"

    type = settings.FEEDBACK_CHOICES[0][0]
    message = factory.fuzzy.FuzzyText(length=100)
    user = factory.SubFactory(UserFactory)
