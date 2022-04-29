from django.urls import re_path

from feedback.api.views import FeedbackCreateView

urlpatterns = [re_path(r"feedbacks/", FeedbackCreateView.as_view())]
