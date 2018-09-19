from django.conf.urls import url
from .charts import RatingsBarChart, FolloweesRatingsBarChart, UserRatingsBarChart
from jchart.views import ChartView

from . import views # import views so we can use them in urls.

app_name = 'reviews'

followees_chart = FolloweesRatingsBarChart()
ratings_chart = RatingsBarChart()
user_ratings_chart = UserRatingsBarChart()

urlpatterns = [
    url(r'^u/(?P<mbid>[0-9a-z-]{36})/$', views.user_review, name='user_review'),
    url(r'^liste/(?P<mbid>[0-9a-z-]{36})/$', views.review_list, name='review_list'),
    url(r'liste/u/(?P<username>[\w_-]{3,})/$', views.user_review_list, name='user_review_list'),
    url(r'^récentes/$', views.latest_reviews, name='latest_reviews'),
    url(r'liste/notes/u/(?P<username>[\w_-]{3,})/$', views.user_rating_list, name='user_rating_list'),   
    url(r'^ajax_vote/$', views.ajax_vote, name='ajax_vote'),
    url(r'^ajax_delete_rating/$', views.ajax_delete_rating, name='ajax_delete_rating'),
    url(r'^charts/followees_chart/(?P<album_id>[0-9]+)/(?P<username>[\w_-]{3,})/$', ChartView.from_chart(followees_chart), name='followees_chart'),
    url(r'^charts/ratings_chart/(?P<album_id>[0-9]+)/$', ChartView.from_chart(ratings_chart), name='ratings_chart'),
    url(r'^charts/user_ratings_chart/(?P<username>[\w_-]{3,})/$', ChartView.from_chart(user_ratings_chart), name='user_ratings_chart'),
    
        ]

