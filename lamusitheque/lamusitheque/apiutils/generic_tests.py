from django.test import TestCase
from rest_framework.test import APIClient


class GenericAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def check_status(self, response, code):
        self.assertEqual(response.status_code, code)

    def login(self, auth):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + auth)

    def object_url(self, id):
        raise NotImplemented

    def list_url(self):
        raise NotImplemented

    def retrieve(self, id, **kwargs):
        return self.client.get(self.object_url(id))

    def list(self, **kwargs):
        return self.client.get(self.list_url())

    def create(self, data, **kwargs):
        return self.client.post(self.list_url(), data=data)

    def update(self, id, data, **kwargs):
        return self.client.put(self.object_url(id), data=data)

    def partial_update(self, id, data, **kwargs):
        return self.client.patch(self.object_url(id), data=data)

    def destroy(self, id, data=None):
        return self.client.delete(self.object_url(id))

    def check_func_not_logged(self, func, id=None, data=None, status_code=200):

        """Check status for an anonymous user,
        and returns response for additional tests"""

        res = func(id=id, data=data)
        self.check_status(res, status_code)
        return res

    def check_func_logged(self, func, auth_key, id=None, data=None, status_code=200):
        self.login(auth_key)
        res = func(id=id, data=data)
        self.check_status(res, status_code)
        return res


