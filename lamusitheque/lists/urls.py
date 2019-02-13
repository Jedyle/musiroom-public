from django.conf.urls import url
from django.urls import reverse, reverse_lazy

from . import views # import views so we can use them in urls.

app_name = 'lists'

urlpatterns = [
    url(r'^(?P<list_id>[0-9]+)/$', views.display_list, name='display_list'),
    url(r'^rechercher/$', views.search_list, name='search_list'),
    url(r'^ajax/lists/$', views.ajax_list, name='ajax_list'),
    url(r'^ajax/items/$', views.ajax_get_items, name='ajax_get_items'),
    url(r'^ajax/move_items/$', views.ajax_move_items, name='ajax_move_items'),
    url(r'^ajax/delete_item/$', views.ajax_delete_item, name='ajax_delete_item'),
    url(r'^ajax/delete_list/$', views.ajax_delete_list, name='ajax_delete_list'),
    url(r'^ajax/user_lists/$', views.ajax_get_lists_for_user, name='ajax_user_lists'),
    url(r'^edit/description/$', views.ajax_set_description, name='ajax_set_description'),
    url(r'^ajax/vote/$', views.ajax_vote, name='ajax_vote'),
    url(r'^ajax/get_lists_for_album/$', views.get_lists_for_user_and_album, name='get_lists_for_user_and_album'),
    url(r'^edit/comment/$', views.ajax_set_item, name='ajax_set_item'),
    url(r'^creer/$', views.create_list, name='create_list'),    
]
