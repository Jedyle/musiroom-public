import re

from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()


@register.simple_tag(takes_context=True)
def active_url(context, url):
    try:
        pattern = '^%s$' % reverse(url)
    except NoReverseMatch:
        pattern = url

    try:
        path = context['request'].path
    except KeyError:
        return ''
    return 'active' if re.search(pattern, path) else ''
