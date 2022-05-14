from django.http import Http404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from albums.scraper import ParseSearchAlbums, ParseSearchArtists
from search.api.serializers import SearchSerializer

from search.methods import AUTOCOMPLETE_SEARCH_METHODS


@api_view(["GET"])
def search(request):
    serializer = SearchSerializer(data=request.GET)
    serializer.is_valid(raise_exception=True)
    method = serializer.validated_data.get("method")
    if method == "auto":
        return autocomplete_search(request)
    else:
        return search_hard(request)


def autocomplete_search(request):
    o_type = request.GET.get("model")
    query = request.GET.get("query")

    search_method = AUTOCOMPLETE_SEARCH_METHODS[o_type]

    res = search_method(query)[:5]

    json_result = []
    for item in res:
        try:
            preview = item.get_preview()
        except AttributeError:
            preview = None
        json_result.append(
            {
                "name": str(item),
                "mbid": item.mbid,
                "preview": preview,
            }
        )
    return Response(json_result)


def search_hard(request):
    query = request.GET.get("query")
    model = request.GET.get("model")
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1
    if not query or not model:
        raise Http404

    search = {"album": ParseSearchAlbums, "artist": ParseSearchArtists}
    parser_class = search.get(model)
    if parser_class is None:
        return Response(
            {"message": "This type is not allowed"}, status=status.HTTP_400_BAD_REQUEST
        )

    parser = parser_class(query, page=page)
    if parser.load():
        results = parser.get_results()
        nb_pages = parser.get_nb_pages()
        return Response({"results": results, "page": page, "num_pages": nb_pages})
    raise Http404
