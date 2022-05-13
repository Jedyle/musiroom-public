from feedback.tests.factories import FeedbackFactory


class TestFeedback:
    def test_str(self):
        feedback = FeedbackFactory()
        assert str(feedback) == feedback.message
