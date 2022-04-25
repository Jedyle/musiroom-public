from .factories import ConversationFactory, MessageFactory


class TestDiscussion:
    def test_str(self):
        conv = ConversationFactory()
        assert str(conv) == str(conv.pk)


class TestMessage:
    def test_str(self):
        msg = MessageFactory()
        assert str(msg) == msg.user.email
