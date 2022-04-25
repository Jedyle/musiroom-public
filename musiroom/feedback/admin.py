from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext

from .models import AnonymousFeedback, Feedback


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'time', 'type']
    search_fields = ['user', 'message']
    list_filter = ['type', 'time']


class AnonymousFeedbackAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'time', 'type']
    search_fields = ['user', 'message']
    list_filter = ['type', 'time']


admin.site.register(Feedback, FeedbackAdmin)
if getattr(settings, 'ALLOW_ANONYMOUS_FEEDBACK', False):
    admin.site.register(AnonymousFeedback, AnonymousFeedbackAdmin)
