from django.conf.urls import url

from . import views # import views so we can use them in urls.

app_name = 'autocomplete_search'

urlpatterns = [
    url(r'^$', views.autocomplete_search, name='autocomplete_search'),
        ]
