from django.test import TestCase


class GenericAPITest(TestCase):

    def check_status(self, response, code):
        self.assertEqual(response.status_code, code)
