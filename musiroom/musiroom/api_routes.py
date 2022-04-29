from django.urls import include, re_path
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.views import get_swagger_view

"""
Top-level router referencing all endpoints for all apps in the project

To add routes from an app:
    from app.api.router import router as app_router
    ...
    router.registry.extends(app_router.registry)

"""

schema_view = get_swagger_view(title="Pastebin API")


api_patterns = [
    re_path(r"^swagger$", schema_view),
    re_path(r"", include("albums.api.urls")),
    re_path(r"", include("user_profile.api.urls")),
    re_path(r"", include("lists.api.urls")),
    re_path(r"", include("star_ratings.api.urls")),
    re_path(r"", include("discussions.api.urls")),
    re_path(r"", include("feedback.api.urls")),
    re_path(r"", include("reviews.api.urls")),
    re_path(r"", include("export_ratings.api.urls")),
    re_path(r"", include("ajax_follower.api.urls")),
    re_path(r"", include("search.api.urls")),
    re_path(r"", include("actstream.api.urls")),
    re_path(r"", include("comments.api.urls")),
    re_path(r"", include("conversations.api.urls"))
    # to add urls from another app : url(r'', include('app.api.urls'))
]

"""
References all api routes, including the ones from external packages
"""

schema_view = get_schema_view(title="Musiroom API")

urlpatterns = [
    re_path(r"schema/", schema_view),
] + api_patterns
