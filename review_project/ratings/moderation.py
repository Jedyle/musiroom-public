from fluent_comments.moderation import FluentCommentsModerator

class UserLoggedInModerator(FluentCommentsModerator):
    
    def allow(self, comment, content_object, request):
        print('user', request.user)
        return request.user.is_authenticated

