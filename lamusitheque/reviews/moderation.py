from fluent_comments.moderation import FluentCommentsModerator

class UserLoggedInModerator(FluentCommentsModerator):
    
    def allow(self, comment, content_object, request):
        return request.user.is_authenticated

