from __future__ import unicode_literals

import django.dispatch

# pre_moderation = django.dispatch.Signal(providing_args=["instance", "status"])

# post_moderation = django.dispatch.Signal(providing_args=["instance", "status"])

# pre_many_moderation = django.dispatch.Signal(providing_args=["queryset", "status", "by", "reason"])

# post_many_moderation = django.dispatch.Signal(providing_args=["queryset", "status", "by", "reason"])

# Django 4 update

pre_moderation = django.dispatch.Signal()

post_moderation = django.dispatch.Signal()

pre_many_moderation = django.dispatch.Signal()

post_many_moderation = django.dispatch.Signal()
