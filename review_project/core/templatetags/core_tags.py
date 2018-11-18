import re

from django import template
from django.urls import reverse, NoReverseMatch
from datetime import date, datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta as rd

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

@register.inclusion_tag('share_box.html', takes_context=True)
def social_share(context, obj):
    context['object'] = obj
    return context

@register.filter
def parse_links(value):
    return re.sub(r'(https://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)', r"<a target='_blank' href='\1'>\1</a>", value)

@register.filter
def smart_date(value):
    if value.date() < date.today():
        return timezone.localtime(value)
    return timezone.localtime(value).time()


def get_time_unit(x, k):
    if getattr(x, k['name']) == 1:
        return k['singular']
    return k['plural']          

@register.filter
def sectotime(s):
    intervals = [
        {
            'name' : 'days',
            'singular' : 'jour',
            'plural' : 'jours',
        },
        {
            'name' : 'hours',
            'singular' : 'heure',
            'plural' : 'heures'
        },
        {
            'name' : 'minutes',
            'singular' : 'minute',
            'plural' : 'minutes',
        },
        {
            'name' : 'seconds',
            'singular' : 'seconde',
            'plural' : 'secondes',
        }
        ]


    x = rd(seconds=s)
    return(' '.join('{} {}'.format(getattr(x,k['name']), get_time_unit(x, k)) for k in intervals if getattr(x,k['name'])))


