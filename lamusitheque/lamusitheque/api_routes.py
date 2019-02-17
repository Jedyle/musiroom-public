from django.conf.urls import url
from django.urls import include
from rest_framework.schemas import get_schema_view

"""
Top-level router referencing all endpoints for all apps in the project

To add routes from an app:
    from app.api.router import router as app_router
    ...
    router.registry.extends(app_router.registry)

"""

api_patterns = [
    url(r'', include("albums.api.urls")),
    url(r'', include("profile.api.urls"))
    # to add urls from another app : url(r'', include('app.api.urls'))
]

"""
References all api routes, including the ones from external packages
"""

schema_view = get_schema_view(title='Lamusitheque API')

urlpatterns = [
    url(r'auth/', include('rest_auth.urls')),
    url(r'schema/', schema_view)
    ] + api_patterns
