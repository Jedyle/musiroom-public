"""
Test authentication with headers.
Test user profile is safe (ex : display_name)
Test
"""
import datetime

from django.contrib.auth.models import User
from rest_framework.test import APIClient, RequestsClient

from lamusitheque.apiutils.generic_tests import GenericAPITest


class AuthenticationTest(GenericAPITest):

    def setUp(self):
        super().setUp()
        self.password = "testmdp"
        self.user = User.objects.create_user(username="toto", password=self.password)

    def test_token_auth(self):
        """
        Test a route that requires authentication, sending token in headers
        """
        res = self.client.post('/api/auth/login/',
                               {
                                   'username': self.user.username,
                                   'password': self.password
                               })
        self.check_status(res, 200)
        auth_key = res.data['key']

        # new client with no credentials or forced login
        self.client = APIClient()

        self.client.credentials()
        res_noauth = self.client.get('/api/auth/user/')
        self.check_status(res_noauth, 401)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + auth_key)
        res_auth = self.client.get('/api/auth/user/')
        self.check_status(res_auth, 200)


class UserProfileTest(GenericAPITest):

    def setUp(self):
        super().setUp()
        self.password = "testmdp"
        self.user = User.objects.create_user(username="toto", password=self.password)
        self.user.profile.birth = datetime.date(1996, 6, 23)
        self.user.profile.sex = 'M'
        self.user.first_name = "Toto"
        self.user.last_name = "Tata"
        self.user.save()
        self.user.profile.save()

    def retrieve_user(self, username):
        return self.client.get('/api/users/' + username + '/')

    def test_display_name_true(self):
        self.user.profile.display_name = True
        self.user.profile.save()
        res = self.retrieve_user(self.user.username)
        name = res.data['name']
        self.assertEqual(name, self.user.first_name + ' ' + self.user.last_name)

    def test_display_name_false(self):
        self.user.profile.display_name = False
        self.user.profile.save()
        res = self.retrieve_user(self.user.username)
        name = res.data['name']
        self.assertEqual(name, None)

    def test_display_sex_true(self):
        self.user.profile.display_sex = True
        self.user.profile.save()
        res = self.retrieve_user(self.user.username)
        sex = res.data['sex']
        self.assertEqual(sex, self.user.profile.get_sex_display())

    def test_display_sex_false(self):
        self.user.profile.display_sex = False
        self.user.profile.save()
        res = self.retrieve_user(self.user.username)
        sex = res.data['sex']
        self.assertEqual(sex, None)

    def test_display_birth_true(self):
        self.user.profile.display_birth = True
        self.user.profile.save()
        res = self.retrieve_user(self.user.username)
        birth = res.data['birth']
        self.assertEqual(birth, self.user.profile.birth)

    def test_display_birth_false(self):
        self.user.profile.display_birth = False
        self.user.profile.save()
        res = self.retrieve_user(self.user.username)
        birth = res.data['birth']
        self.assertEqual(birth, None)

