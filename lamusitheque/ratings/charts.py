from jchart import Chart
from star_ratings.models import UserRating
from django.contrib.auth.models import User
from albums.models import Album
from django.db.models import Q

class FolloweesRatingsBarChart(Chart):
    chart_type = 'bar'
    title = {
        'display' : True,
        'text' : 'Notes de mes abonnements'
        }
    legend = { 'display' : False }
    scales = {
        'yAxes' : [{
            'ticks' : {
                'stepSize' : 1,
                'beginAtZero' : True,
                'display' : False,
                },
            'gridLines': {
                    'display' : False,
                } 
            }]
        }
    tooltips = {
        'mode' : 'point',
        }
    
    def get_datasets(self, album_id, username):
        album = Album.objects.get(pk = album_id)
        user = User.objects.get(username = username) 
        ratings = UserRating.objects.filter(Q(rating__albums = album) & Q(user__followers__follower = user))
        count = [0 for i in range(10)]
        for rating in ratings :
            count[rating.score-1]+=1
        return [{
            'data': count ,
            'backgroundColor' : ["#009997","#009997","#009997","#009997","#009997","#009997","#009997","#009997","#009997","#009997"],
        }]

    def get_labels(self, *args, **kwargs):
        return ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]



class RatingsBarChart(Chart):
    chart_type = 'bar'
    title = {
        'display' : True,
        'text' : 'Répartition des notes'
        }
    legend = { 'display' : False }
    scales = {
        'yAxes' : [{
            'ticks' : {
                'stepSize' : 1,
                'beginAtZero' : True,
                'display' : False,
                },
            'gridLines': {
                    'display' : False,
                } 
            }]
        }
    tooltips = {
        'mode' : 'point',
        }
    
    def get_datasets(self, album_id):
        album = Album.objects.get(pk = album_id)
        ratings = UserRating.objects.filter(Q(rating__albums = album))
        count = []
        for i in range(10) :
            count.append(ratings.filter(score = i+1).count())
        return [{
            'data': count ,
            'backgroundColor' : ["#808080","#808080","#808080","#808080","#808080","#808080","#808080","#808080","#808080","#808080"]
        }]

    def get_labels(self, *args, **kwargs):
        return ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]


class UserRatingsBarChart(Chart):
    chart_type = 'bar'
    title = {
        'display' : True,
        'text' : 'Répartition des notes'
        }
    legend = { 'display' : False }
    scales = {
        'yAxes' : [{
            'ticks' : {
                'stepSize' : 1,
                'beginAtZero' : True,
                'display' : False,
                },
            'gridLines': {
                    'display' : False,
                } 
            }]
        }
    tooltips = {
        'mode' : 'point',
        }
    
    def get_datasets(self, username):
        user = User.objects.get(username = username)
        count = []
        for i in range(10) :
            count.append(UserRating.objects.filter(user = user).filter(score = i).count())
        return [{
            'data': count ,
            'backgroundColor' : ["#ffffff","#aaaaaa","#aaaaaa","#aaaaaa","#aaaaaa","#aaaaaa","#aaaaaa","#aaaaaa","#aaaaaa","#aaaaaa"]
        }]

    def get_labels(self, *args, **kwargs):
        return ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
