from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from albums.models import Album
from ratings.models import Review
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from star_ratings.models import UserRating
from django.urls import reverse

# Create your views here.

def home(request):
    time_threshold = datetime.now() - timedelta(days=60)
    new_albums = Album.objects.filter(release_date__gt=time_threshold).filter(ratings__isnull = False).order_by('-ratings__count')[:18]
    reviews = Review.objects.all().order_by('-date_publication')[:10]
    ratings = UserRating.objects.all().order_by('-modified')[:10]
    context = {
        'albums' : new_albums,
        'reviews' : reviews,
        'ratings' : ratings,
        }
    return render(request, 'core/home.html', context)

@login_required
def ajax_followees_reviews(request):
    followees_reviews = Review.objects.filter(rating__user__followers__follower = request.user).order_by('-date_publication')[:10]
    reviews = []
    for review in followees_reviews:
        album = review.rating.rating.albums.get()
        username = review.rating.user.username
        reviews.append({
            'mbid' : album.mbid,
            'title' : album.title,
            'cover' : album.get_cover(),
            'username' : username,
            'score' : review.rating.score,
            'review_title' : review.title,
            'album_url' : reverse('albums:album', args=[album.mbid]),
            'profile_url' : reverse('profile', args=[username]),
            'review_url' : reverse('albums:review', args=[album.mbid, review.id]),
            'avatar' : review.rating.user.account.get_avatar(),
            })
    context = {
        'reviews' : reviews,
        }
    return JsonResponse(context)
    
@login_required
def ajax_followees_ratings(request):
    followees_ratings = UserRating.objects.filter(user__followers__follower = request.user).order_by('-modified')[:10]
    ratings = []
    for rating in followees_ratings:
        album = rating.rating.albums.get()
        username = rating.user.username
        ratings.append({
            'score' : rating.score,
            'username' : username,
            'mbid' : album.mbid,
            'cover' : album.get_cover(),
            'title' : album.title,
            'album_url' : reverse('albums:album', args=[album.mbid]),
            'profile_url' : reverse('profile', args=[username]),
            'avatar' : rating.user.account.get_avatar(),
            })
    context = {
        'ratings' : ratings,
        }
    return JsonResponse(context)
