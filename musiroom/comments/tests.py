from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from comments.models import Comment
from conversations.models import Conversation
from musiroom.apiutils.generic_tests import GenericAPITest

# Create your tests here.

"""
PERMISSIONS : 

* update comment not logged in OK
* update comment wrong user OK
* update comment right user OK
* idem patch, delete OK
* comments on unauthorized objects


"""


class CommentViewsetSet(GenericAPITest):
    def setUp(self):
        super().setUp()
        self.password = "testmdp"
        self.user1 = User.objects.create_user("test1", self.password)
        self.user2 = User.objects.create_user("test2", self.password)
        self.comment1 = Comment.objects.create(
            content_object=self.user1.profile.top_albums,
            user=self.user2,
            comment="this is a test",
        )

    def list_url(self):
        return "/api/comments/"

    def object_url(self, id):
        return "/api/comments/{}/".format(id)

    def test_list_comments(self):
        self.check_func_not_logged(self.list, status_code=200)

    def test_retrieve_commment(self):
        c_id = self.comment1.id
        self.check_func_not_logged(self.retrieve, id=c_id, status_code=200)

    def test_create_comment_unauthorized(self):
        # comment a list
        content_object = self.user2.profile.top_albums
        comment_text = "this is a test 2"
        data = {
            "content_type": ContentType.objects.get_for_model(content_object).model,
            "object_pk": content_object.id,
            "comment": comment_text,
            "parent": "",  # forces APIClient to send None
        }
        self.check_func_not_logged(self.create, data=data, status_code=401)

    def test_create_comment_loggedin(self):
        """
        Test a comment can't be created if not logged in
        """
        content_object = self.user2.profile.top_albums
        comment_text = "this is a test 2"
        data = {
            "content_type": ContentType.objects.get_for_model(content_object).model,
            "object_pk": content_object.id,
            "comment": comment_text,
            "parent": "",  # forces APIClient to send None
        }
        self.check_func_logged(
            self.create, auth_key=self.user1.auth_token.key, data=data, status_code=201
        )

    def check_affect_comment_no_auth(self, func, data):
        comment_id = self.comment1.id
        self.check_func_not_logged(func, data=data, status_code=401)

    def check_affect_comment_wrong_auth(self, func, data):
        # comment belong to user2
        comment_id = self.comment1.id
        # login with user 1
        self.check_func_logged(
            func,
            id=comment_id,
            auth_key=self.user1.auth_token.key,
            data=data,
            status_code=403,
        )

    def check_affect_comment_right_auth(self, func, data, status=200):
        # comment belong to user2
        comment_id = self.comment1.id
        # login with user 1
        self.check_func_logged(
            func,
            id=comment_id,
            auth_key=self.user2.auth_token.key,
            data=data,
            status_code=status,
        )

    def test_update_auth(self):
        data = {"comment": "This is a modification !"}
        func = self.update
        self.check_affect_comment_no_auth(func, data)
        self.check_affect_comment_wrong_auth(func, data)
        self.check_affect_comment_right_auth(func, data)

    def test_partial_update_auth(self):
        data = {"comment": "This is a modification !"}
        func = self.partial_update
        self.check_affect_comment_no_auth(func, data)
        self.check_affect_comment_wrong_auth(func, data)
        self.check_affect_comment_right_auth(func, data)

    def test_delete_auth(self):
        data = {"comment": "This is a modification !"}
        func = self.destroy
        self.check_affect_comment_no_auth(func, data)
        self.check_affect_comment_wrong_auth(func, data)
        # warning : after this line a comment is deleted
        # so we can't use it anymore in this test
        self.check_affect_comment_right_auth(func, data, status=204)

    def test_create_comment_on_unauthorized_object(self):
        unauthorized_obj = Conversation.objects.create(title="Test conv")
        unauthorized_obj.users.add(self.user1, self.user2)
        unauthorized_obj.save()
        self.login(self.user1.auth_token.key)
        res = self.create(
            {
                "content_type": ContentType.objects.get_for_model(
                    unauthorized_obj
                ).model,
                "object_pk": unauthorized_obj.id,
                "comment": "hello",
                "parent": "",  # forces APIClient to send None
            }
        )
        self.check_status(res, 400)
