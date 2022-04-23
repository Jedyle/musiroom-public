from rest_framework import status
from user_profile.tests.factories import UserFactory
from conversations.tests.factories import ConversationFactory, MembershipFactory


class TestConversationList:

    URL = "/api/conversations/"

    def test_list_not_logged(self, client):
        response = client.get(self.URL)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_logged(self, client):
        user = UserFactory()
        client.force_login(user)
        conversations = ConversationFactory.create_batch(5)
        for conv in conversations:
            MembershipFactory(user=user, conversation=conv)
            conv.save()
        response = client.get(self.URL)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()["results"]) == 5


class TestConversationRetrieve:

    URL = "/api/conversations/{}/"

    def test_retrieve_not_logged(self, client):
        conversation = ConversationFactory()
        response = client.get(self.URL.format(conversation.pk))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_bad_login(self, client):
        user = UserFactory()
        client.force_login(user)
        conversation = ConversationFactory()
        response = client.get(self.URL.format(conversation.pk))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_retrieve_login_ok(self, client):
        user = UserFactory()
        client.force_login(user)
        conversation = ConversationFactory()
        MembershipFactory(conversation=conversation, user=user)
        response = client.get(self.URL.format(conversation.pk))
        assert response.status_code == status.HTTP_200_OK
