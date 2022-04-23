import pytest

from rest_framework import status


class TestRegisterView:

    URL = "/api/registration/"

    @staticmethod
    @pytest.fixture
    def mock_celery_send_email(mocker):
        return mocker.patch("user_profile.tasks.send_user_activation_email.delay")

    @staticmethod
    @pytest.fixture
    def mock_transaction(mocker):
        return mocker.patch(
            "user_profile.api.views.transaction.on_commit", new=lambda fn: fn()
        )

    def test_ok(
        self,
        client,
        mocker,
        mock_transaction,
        mock_celery_send_email,
        django_user_model,
    ):
        userdata = {
            "email": "jeremy.lixandre@gmail.com",
            "username": "fakeuser",
            "password": "fakepassword",
            "password_confirm": "fakepassword",
        }
        response = client.post(self.URL, data=userdata, content_type="application/json")
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        mock_celery_send_email.assert_called_once_with("fakeuser")
        user = django_user_model.objects.get(username="fakeuser")
        assert user.is_active is False
        assert user.profile

    def test_passwords_dont_match(
        self,
        client,
        mocker,
        mock_transaction,
        mock_celery_send_email,
        django_user_model,
    ):
        userdata = {
            "email": "jeremy.lixandre@gmail.com",
            "username": "fakeuser",
            "password": "fakepassword",
            "password_confirm": "fakepassword2",
        }
        response = client.post(self.URL, data=userdata, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        mock_celery_send_email.assert_not_called()
        assert not django_user_model.objects.filter(username="fakeuser").exists()

    def test_username_exists(
        self,
        client,
        mocker,
        mock_transaction,
        mock_celery_send_email,
        django_user_model,
    ):
        django_user_model.objects.create(username="fakeuser", password="fakepass")
        userdata = {
            "email": "jeremy.lixandre@gmail.com",
            "username": "fakeuser",
            "password": "fakepassword",
            "password_confirm": "fakepassword",
        }
        response = client.post(self.URL, data=userdata, content_type="application/json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        mock_celery_send_email.assert_not_called()
