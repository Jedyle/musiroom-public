from django.contrib import admin

from .models import Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ["user", "message", "time", "type"]
    search_fields = ["user", "message"]
    list_filter = ["type", "time"]


admin.site.register(Feedback, FeedbackAdmin)
