import re

from django import template
from django.urls import reverse, NoReverseMatch
from datetime import date, datetime
from django.utils import timezone

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

@register.inclusion_tag('popover_scripts.html')
def include_popover_scripts():
    return {}

@register.filter
def parse_links(value):
    return re.sub(r'(https://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', r"<a target='_blank' href='\1'>\1</a>", value)

@register.filter
def smart_date(value):
    if value.date() < date.today():
        return timezone.localtime(value)
    return timezone.localtime(value).time()
