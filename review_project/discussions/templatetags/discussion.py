from django import template
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from discussions.models import Discussion
from discussions.register import discussions_registry

register = template.Library()

@register.filter
def content_type(obj):
    if not obj:
        return None
    return ContentType.objects.get_for_model(obj)

@register.filter
def is_instance_of(obj, string):
    return str(ContentType.objects.get_for_model(obj)) == string

@register.filter
def content_type_pk(obj):
    if not obj:
        return 0
    return ContentType.objects.get_for_model(obj).pk


@register.filter
def get_vote(object, user):
    if (object.votes.exists(user.id, action = 0)):
        return 'up'
    elif (object.votes.exists(user.id, action = 1)):
        return 'down'
    else:
        return 'none'

@register.simple_tag
def get_discussion_content_types():
    return [ContentType.objects.get_for_model(model) for model in discussions_registry._registry]

@register.inclusion_tag('discussions/latest_discussions.html')
def get_last_discussions(obj, nb):
    ct = ContentType.objects.get_for_model(obj)
    discussions = Discussion.objects.filter(content_type = ct, object_id = obj.pk)[:nb]
    return {'discussions' : discussions}
