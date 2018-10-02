"""review_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static

from core import views

urlpatterns = [
    url(r'^manage/', admin.site.urls),
    url(r'^$', views.home, name = 'home'),
    url(r'^live$', views.feed, name='live'),
    url(r'^home_followees_reviews/', views.ajax_followees_reviews, name="home_followees_reviews"),
    url(r'^home_followees_ratings/', views.ajax_followees_ratings, name="home_followees_ratings"),
    url(r'^profil/',  include('account.urls')),
    url(r'^messages/', include('postman.urls', namespace='postman')),
    url(r'^musique/', include('albums.urls', namespace='albums')),
    url(r'^notes/', include('star_ratings.urls', namespace='ratings')),
    url(r'^critiques/', include('ratings.urls', namespace='reviews')),
    url(r'^commentaires/', include('django_comments_xtd.urls')),
    url(r'^contacts/', include('friendship.urls')),
    url(r'^suivre/', include('ajax_follower.urls')),
    url(r'^listes/', include('lists.urls', namespace='lists')),
    url(r'^notifications/', include('notifications.urls', namespace='notifications')),
    url(r'^feedback/', include('feedback.urls', namespace='feedback')),
    url(r'^discussions/', include('discussions.urls', namespace='discussions')),
    url(r'^autocomplete/', include('autocomplete_search.urls', namespace='autocomplete_search')),
    url(r"^badges/", include("pinax.badges.urls", namespace="pinax_badges")),
    url(r'^activité/', include('actstream.urls')),
    ]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
