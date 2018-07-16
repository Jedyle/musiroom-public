from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.template.loader import render_to_string
from albums.models import Album
from ratings.models import Review
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from star_ratings.models import UserRating

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
    context = {
        'reviews' : followees_reviews,
        }
    rendered = render_to_string('core/reviews.html', context, request=request)
    return HttpResponse(rendered)
    
@login_required
def ajax_followees_ratings(request):
    followees_ratings = UserRating.objects.filter(user__followers__follower = request.user).order_by('-modified')[:10]
    context = {
        'ratings' : followees_ratings,
        }
    rendered = render_to_string('core/ratings.html', context, request=request)
    return HttpResponse(rendered)
