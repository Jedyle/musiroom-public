from django.contrib.contenttypes.models import ContentType

def same_notifications(queryset, actor, verb, target = None):
    if target is not None:
        return queryset.filter(actor_content_type = ContentType.objects.get_for_model(actor), actor_object_id = actor.id, verb = verb, target_content_type = ContentType.objects.get_for_model(target), target_object_id = target.id)
    else:
        return queryset.filter(actor_content_type = ContentType.objects.get_for_model(actor), actor_object_id = actor.id, verb = verb, target_content_type = None, target_object_id = None)

