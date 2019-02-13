from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view
from albums.api.router import router as album_router

"""
Top-level router referencing all endpoints for all apps in the project

To add routes from an app:
    from app.api.router import router as app_router
    ...
    router.registry.extends(app_router.registry)

"""

router = DefaultRouter()
router.registry.extend(album_router.registry)


"""
References all api routes, including the ones from external packages
"""

schema_view = get_schema_view(title='Lamusitheque API')

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'auth/', include('rest_auth.urls')),
    url(r'schema/', schema_view),
]
