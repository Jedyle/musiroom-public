from django.conf.urls import url

from feedback.api.views import FeedbackCreateView

urlpatterns = [
    url(r'feedbacks/', FeedbackCreateView.as_view())
]
