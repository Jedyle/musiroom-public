from rest_framework import status
from user_profile.tests.factories import UserFactory


class TestFeedbackView:

    URL = "/api/feedbacks/"

    def test_create_feedback_msg_too_short(self, client):
        data = {"type": "bug", "message": ""}
        response = client.post(self.URL, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        json_res = response.json()
        assert "message" in json_res

    def test_create_feedback_anonymous(self, client):
        data = {"type": "bug", "message": "mock mock mock mock"}
        response = client.post(self.URL, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED
        json_res = response.json()
        assert json_res["type"] == data["type"]
        assert json_res["message"] == data["message"]
        assert json_res["user"] is None

    def test_create_feedback_logged(self, client):
        user = UserFactory()
        client.force_login(user)
        data = {"type": "bug", "message": "mock mock mock mock"}
        response = client.post(self.URL, data=data, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED
        json_res = response.json()
        assert json_res["type"] == data["type"]
        assert json_res["message"] == data["message"]
        assert json_res["user"] == user.username
