from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from albums.scraper import ParseSearchAlbums, get_page_list, ParseSearchArtists
from search.api.serializers import SearchSerializer
from search.settings import get_search_config, DEFAULT_SEARCH_FIELD


@api_view(['GET'])
def search(request):
    serializer = SearchSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    method = serializer.validated_data.get('method')
    if method == "auto":
        return autocomplete_search(request)
    else:
        return search_hard(request)


def autocomplete_search(request):
    o_type = request.GET.get('model')
    query = request.GET.get('query')

    search_conf = get_search_config()
    model_search_field = search_conf.get(o_type, DEFAULT_SEARCH_FIELD)

    ct = ContentType.objects.get(model=o_type.lower())
    Model = ct.model_class()

    res = Model.objects.filter(**{model_search_field + '__icontains': query})[:5]

    json_result = []
    for item in res:
        try:
            preview = item.get_preview()
        except AttributeError:
            preview = None
        json_result.append({
            'name': str(item),
            'mbid': item.mbid,
            'preview': preview,
        })
    return Response(json_result)


def search_hard(request):
    query = request.GET.get('query')
    model = request.GET.get('model')
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1
    if not query or not model:
        raise Http404

    search = {
        "album": ParseSearchAlbums,
        "artist": ParseSearchArtists
    }
    parser_class = search.get(model)
    if parser_class is None:
        return Response({
            "message": "This type is not allowed"
        }, status=status.HTTP_400_BAD_REQUEST)

    parser = parser_class(query, page=page)
    if parser.load():
        results = parser.get_results()
        nb_pages = parser.get_nb_pages()
        return Response({
            "results": results,
            "page": page,
            "num_pages": nb_pages
        })
    raise Http404
