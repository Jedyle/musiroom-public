
from .charts import RatingsBarChart, FolloweesRatingsBarChart, UserRatingsBarChart

app_name = 'reviews'

followees_chart = FolloweesRatingsBarChart()
ratings_chart = RatingsBarChart()
user_ratings_chart = UserRatingsBarChart()

urlpatterns = []
