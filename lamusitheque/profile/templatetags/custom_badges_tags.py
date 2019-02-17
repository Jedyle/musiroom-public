from django import template
from pinax.badges.models import BadgeAward

register = template.Library()


@register.filter
def badge_image(award):
    try:
        img = award._badge.images[award.level]
        return img
    except IndexError:
        return ""


@register.simple_tag
def distinct_badges_for_user(user):
    return BadgeAward.objects.filter(user=user).order_by('slug', '-level').distinct('slug')
