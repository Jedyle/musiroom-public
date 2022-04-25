from django.conf.urls import url
from django.urls import include
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
    url(r"^swagger$", schema_view),
    url(r"", include("albums.api.urls")),
    url(r"", include("user_profile.api.urls")),
    url(r"", include("lists.api.urls")),
    url(r"", include("star_ratings.api.urls")),
    url(r"", include("discussions.api.urls")),
    url(r"", include("feedback.api.urls")),
    url(r"", include("reviews.api.urls")),
    url(r"", include("export_ratings.api.urls")),
    url(r"", include("ajax_follower.api.urls")),
    url(r"", include("search.api.urls")),
    url(r"", include("actstream.api.urls")),
    url(r"", include("comments.api.urls")),
    url(r"", include("conversations.api.urls"))
    # to add urls from another app : url(r'', include('app.api.urls'))
]

"""
References all api routes, including the ones from external packages
"""

schema_view = get_schema_view(title="Musiroom API")

urlpatterns = [
    url(r"auth/", include("rest_auth.urls")),
    url(r"schema/", schema_view),
] + api_patterns
