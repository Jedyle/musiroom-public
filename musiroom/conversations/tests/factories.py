import factory
import factory.fuzzy

from user_profile.tests.factories import UserFactory


class ConversationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "conversations.Conversation"

    title = factory.fuzzy.FuzzyText(length=50)


class MessageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "conversations.Message"

    conversation = factory.SubFactory(ConversationFactory)
    text = factory.fuzzy.FuzzyText(length=100)
    user = factory.SubFactory(UserFactory)


class MembershipFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "conversations.Membership"
