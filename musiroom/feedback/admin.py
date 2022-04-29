from django.conf import settings
from django.contrib import admin

from .models import AnonymousFeedback, Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "time", "type"]
    search_fields = ["user", "message"]
    list_filter = ["type", "time"]


class AnonymousFeedbackAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "time", "type"]
    search_fields = ["user", "message"]
    list_filter = ["type", "time"]


admin.site.register(Feedback, FeedbackAdmin)
if getattr(settings, "ALLOW_ANONYMOUS_FEEDBACK", False):
    admin.site.register(AnonymousFeedback, AnonymousFeedbackAdmin)
