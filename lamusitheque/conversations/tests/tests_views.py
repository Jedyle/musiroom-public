from django.contrib.auth.models import User

from conversations.models import Conversation, Message
from lamusitheque.apiutils.generic_tests import GenericAPITest


class TestConversationViewset(GenericAPITest):

    def object_url(self, id):
        return "/api/conversations/{}/".format(id)

    def list_url(self):
        return "/api/conversations/"

    def setUp(self):
        super().setUp()
        self.user1 = User.objects.create_user(username="toto", password="testmdp")
        self.user2 = User.objects.create_user(username="tata", password="testmdp")
        self.user3 = User.objects.create_user(username="titi", password="testmdp")
        self.conversation = Conversation.objects.create(title="Test conv")
        self.conversation.users.add(self.user1, self.user2)
        self.conversation.save()
        self.messages = [
            Message.objects.create(conversation=self.conversation, text="Hello how are u ?", user=self.user1),
            Message.objects.create(conversation=self.conversation, text="Fine thanks!", user=self.user2)
        ]

    def test_conversation_list_not_logged(self):
        self.check_func_not_logged(self.list, status_code=401)

    def test_conversation_list_logged(self):
        self.check_func_logged(self.list, auth_key=self.user3.auth_token.key, status_code=200)

    def test_retrieve_conversation_not_logged(self):
        self.check_func_not_logged(self.retrieve, id=self.conversation.id, status_code=401)

    def test_retrieve_conversation_wrong_auth(self):
        # try to retrieve conversation when the user is not in it
        self.check_func_logged(self.retrieve, id=self.conversation.id,
                               auth_key=self.user3.auth_token.key, status_code=404)

    def test_retrieve_conversation_right_auth(self):
        self.check_func_logged(self.retrieve, id=self.conversation.id,
                               auth_key=self.user2.auth_token.key, status_code=200)
