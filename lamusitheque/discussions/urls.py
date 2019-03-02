from django.conf.urls import url

from . import views # import views so we can use them in urls.

app_name = 'discussions'

urlpatterns = [
    # url(r'^$', views.search_discussion_for_object, name='search_discussion_for_object'),
    # url(r'^rechercher/$', views.ajax_search_object, name='ajax_search_object'),
    # url(r'^creer/$', views.create_discussion, name='create_discussion'),
    # url(r'^(?P<content_id>[0-9]+)/(?P<object_id>[0-9]+)/creer/$', views.create_discussion, name='create_discussion'),
    # url(r'^(?P<content_id>[0-9]+)/(?P<object_id>[0-9]+)/toutes/$', views.search_discussion_for_object, name='search_discussion_for_object'),
    # url(r'^d/(?P<id>[0-9]+)/$', views.display_discussion, name='display_discussion'),
    # url(r'^editer/(?P<id>[0-9]+)/$', views.edit_discussion, name='edit_discussion'),
    # url(r'^confirmer_suppression/(?P<id>[0-9]+)/$', views.confirm_delete, name='confirm_delete'),
    # url(r'^supprimer/(?P<id>[0-9]+)/$', views.delete_discussion, name='delete_discussion'),
    # url(r'^vote/$', views.ajax_vote, name='ajax_vote'),
    # url(r'^ajax/user_discussions/$', views.ajax_get_discussions_for_user, name='ajax_user_discussions')
        ]
