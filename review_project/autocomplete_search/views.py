from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.urls import reverse
from .settings import get_search_config, DEFAULT_SEARCH_FIELD

# Create your views here.

def autocomplete_search(request):

    o_type = request.GET.get('model')
    query = request.GET.get('query')

    search_conf = get_search_config()
    model_search_field = search_conf.get(o_type, DEFAULT_SEARCH_FIELD)

    ct = ContentType.objects.get(model = o_type.lower())
    Model = ct.model_class()

    res = Model.objects.filter(**{ model_search_field + '__icontains' : query })[:5]

    json_result = []
    for item in res:
        try:
            preview = item.get_preview()
        except AttributeError:
            preview = None
        json_result.append({
            'name' : str(item),
            'url' : item.get_absolute_url(),
            'preview' : preview,
            })
    return JsonResponse(json_result, safe=False)
