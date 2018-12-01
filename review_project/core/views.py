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
from django.db.models import Max, Q
from django.db.models import Prefetch
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from actstream.models import user_stream, Action
from django.conf import settings
from core.settings import DEFAULT_ACTIVITY_ITEMS_PER_PAGE

# Create your views here.

def home(request):
    time_threshold = datetime.now() - timedelta(days=30)
    new_albums = Album.objects.filter(release_date__gt=time_threshold).filter(ratings__isnull = False).exclude(cover = "").exclude(cover__isnull=True).order_by('-ratings__count')[:12]
    reviews = compute_reviews_feed()
    ratings = compute_ratings_feed()
    user_feed = compute_user_stream(request)
    all_feed = compute_general_stream()
    print(user_feed)
    print(reviews)
    print(ratings)
    context = {
        'albums' : new_albums,
        'reviews' : reviews,
        'ratings' : ratings,
        'user_feed' : user_feed,
        'all_feed' : all_feed,
        }
    if request.user.is_authenticated:
        return render(request, 'core/home.html', context)
    else:
        return render(request, 'core/home_guest.html', context)

def compute_general_stream():
    stream = Action.objects.all()
    num_items = getattr(settings, 'ACTIVITY_ITEMS_PER_PAGE', DEFAULT_ACTIVITY_ITEMS_PER_PAGE)
    p = Paginator(stream, num_items)
    return p.page(1)


def compute_user_stream(request):
    if request.user.is_authenticated:
        stream = user_stream(request.user)
        num_items = getattr(settings, 'ACTIVITY_ITEMS_PER_PAGE', DEFAULT_ACTIVITY_ITEMS_PER_PAGE)
        p = Paginator(stream, num_items)
        return p.page(1)
    return None

DATE = datetime.now() - timedelta(days = 5)
DATE_REVIEWS = datetime.now() - timedelta(days = 30)

def compute_reviews_feed():
    users = User.objects.filter(userrating__review__isnull=False, userrating__review__date_publication__gt=DATE_REVIEWS).distinct().annotate(last_date = Max('userrating__review__date_publication')).order_by('-last_date').select_related('account')

    user_list = users[:4]

    user_reviews = []
    for user in user_list:
        reviews = Review.objects.filter(Q(rating__user=user) & Q(date_publication__gt = DATE_REVIEWS)).order_by('-date_publication').prefetch_related('rating__rating__content_object')[:15]
        user_reviews.append({
            'user' : user,
            'account' : user.account, #mis car select related ne marche pas ...
            'reviews' : reviews,
            })
    return user_reviews

def compute_ratings_feed():
    users = User.objects.filter(userrating__isnull=False, userrating__modified__gt=DATE).annotate(last_date = Max('userrating__modified')).order_by('-last_date').select_related('account')
    user_list = users[:4]

    user_ratings = []
    for user in user_list:
        ratings = UserRating.objects.filter(Q(user=user) & Q(modified__gt = DATE)).order_by('-modified').prefetch_related('rating__content_object')[:15]
        user_ratings.append({
            'user' : user,
            'account' : user.account, #mis car select related ne marche pas ...
            'ratings' : ratings,
            })
    return user_ratings


@login_required
def ajax_followees_reviews(request):
    users = User.objects.filter(followers__follower = request.user, userrating__review__isnull=False, userrating__review__date_publication__gt=DATE_REVIEWS).annotate(last_date = Max('userrating__review__date_publication')).order_by('-last_date').select_related('account')
    user_list = users[:4]

    user_reviews = []
    for user in user_list:
        reviews = Review.objects.filter(Q(rating__user=user) & Q(date_publication__gt = DATE_REVIEWS)).order_by('-date_publication').prefetch_related('rating__rating__content_object')[:15]
        reviews_data = []
        for rev in reviews:
            album = rev.rating.rating.content_object
            reviews_data.append({
                'mbid' : album.mbid,
                'title' : album.title,
                'review_url' : reverse('albums:review', args=[album.mbid, rev.id]),
                'score' : rev.rating.score,
                'review_title' : rev.title,
                'album_url' : reverse('albums:album', args=[album.mbid]),
                })
        user_reviews.append({
            'username' : user.username,
            'profile_url' : reverse('profile', args=[user.username]),
            'avatar' : user.account.get_avatar(),
            'reviews' : reviews_data,
            })
    return JsonResponse({'users' : user_reviews})
    
@login_required
def ajax_followees_ratings(request):
    users = User.objects.filter(followers__follower = request.user, userrating__isnull=False, userrating__modified__gt=DATE).annotate(last_date = Max('userrating__modified')).order_by('-last_date').select_related('account')
    user_list = users[:4]

    user_ratings = []
    for user in user_list:
        ratings = UserRating.objects.filter(Q(user=user) & Q(modified__gt = DATE)).order_by('-modified').prefetch_related('rating__content_object')[:15]
        ratings_data = []
        for rat in ratings:
            album = rat.rating.content_object
            ratings_data.append({
                'mbid' : album.mbid,
                'title' : album.title,
                'score' : rat.score,
                'album_url' : reverse('albums:album', args=[album.mbid]),
                })
        user_ratings.append({
            'username' : user.username,
            'profile_url' : reverse('profile', args=[user.username]),
            'avatar' : user.account.get_avatar(),
            'ratings' : ratings_data,
            })
    return JsonResponse({'users' : user_ratings})


@login_required
def feed(request):
    page = request.GET.get('page', 1)
    feed_type = request.GET.get('feed', 'tout')
    if feed_type == 'abonnements':
        stream = user_stream(request.user)
    else:
        stream = Action.objects.all()
    num_items = getattr(settings, 'ACTIVITY_ITEMS_PER_PAGE', DEFAULT_ACTIVITY_ITEMS_PER_PAGE)
    p = Paginator(stream, num_items)
    try:
        feed = p.page(page)
    except PageNotAnInteger:
        feed = p.page(1)
    except EmptyPage:
        feed = p.page(paginate.num_pages)
    context = {
        'feed' : feed,
        'feed_type' : feed_type,
        }
    return render(request, 'core/feed.html', context)
