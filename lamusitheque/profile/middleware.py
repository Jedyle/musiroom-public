from django.utils import timezone


class UpdateLastActivityMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        assert hasattr(request,
                       'user'), 'The UpdateLastActivityMiddleware requires authentication middleware to be installed.'
        if request.user.is_authenticated:
            account = request.user.profile
            account.last_activity = timezone.now()
            account.save()
