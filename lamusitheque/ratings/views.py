from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, QueryDict
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from star_ratings.models import UserRating
from albums.models import Album, UserInterest
from .models import Review
from .forms import ReviewForm
from .utils import rating_for_followees
from albums.views import compute_sidebar_args
from django.db.models import Q, Avg
from math import ceil
from django.template.defaultfilters import floatformat
from notifications.signals import notify
from profile.utils import same_notifications
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from albums.scraper import get_page_list

# Create your views here.
        
@login_required
def user_review(request, mbid):
    method = request.method
    try:
        instance = Album.objects.get(mbid = mbid)
    except Album.DoesNotExist:
        instance = None
    if method == 'POST': #create review
        try:
            user_rating = UserRating.objects.for_instance_by_user(instance, user=request.user)
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                title = review_form.cleaned_data.get('title')
                if title == 'undefined':
                    title = "Critique de " + request.user.username + " sur " + instance.title
                content = review_form.cleaned_data.get('content')
                try:
                    old_review = user_rating.review
                    old_review.title = title
                    old_review.content = content
                    old_review.save()
                    # user_rating.save()
                except Review.DoesNotExist:
                    review = Review(title = title, content = content, rating=user_rating)
                    # user_rating.review = review
                    # user_rating.save()
                    review.save()
                url = reverse('albums:review', args=[mbid, user_rating.review.pk])
                return JsonResponse({'url' : url})
            else:
                return HttpResponseNotFound()
        except UserRating.DoesNotExist:
            return HttpResponseNotFound()
    elif method == 'GET': #get review from logged in user
        try:
            user_rating = UserRating.objects.for_instance_by_user(instance, user=request.user)
            review = user_rating.review
            data = {
                'title': review.title,
                'content' : review.content,
                'exists' : True,
                }
            return JsonResponse(data)
        except (UserRating.DoesNotExist) :
            return HttpResponseNotFound()
        except (Review.DoesNotExist):
            return JsonResponse({'exists' : False})
    elif method == 'DELETE':
        try:
            user_rating = UserRating.objects.for_instance_by_user(instance, user=request.user)
            review = user_rating.review
            review.delete()
            return JsonResponse({})
        except (UserRating.DoesNotExist, Review.DoesNotExist) :
            return HttpResponseNotFound()            
    return HttpResponseNotFound()


def get_vote(review, user):
    if (review.votes.exists(user.id, action = 0)): #up
        return "up"
    elif (review.votes.exists(user.id, action = 1)): #down
        return "down"
    else:
        return "none"

def review(request, mbid, review_id):
    review = get_object_or_404(Review, pk = review_id)
    album = Album.objects.get(mbid = mbid)
    
    if (review.rating.rating.content_object != album):
        return HttpResponseNotFound()

    context = compute_sidebar_args(album)

    context['review'] = review
    context['r_user'] = review.rating.user

    if request.user.is_authenticated :
        user = User.objects.get(id = request.user.id)
        context['user_vote'] = get_vote(review, user)

    return render(request, 'ratings/review.html', context)

def search_review_by_user(result, query):
    words = query.split(' ')
    for word in words :
        result = result.filter(Q(rating__user__username__icontains = word) | Q(title__icontains = word))
    return result.distinct()

def review_list(request, mbid):
    if request.method == 'GET':
        sort_method = request.GET['methode']
        try : 
            page = int(request.GET['page'])
        except ValueError :
            page = 1
        if page <= 0:
            page = 1
        album = Album.objects.get(mbid = mbid)
        all_reviews = Review.objects.filter(rating__rating__object_id = album.id, rating__rating__content_type = ContentType.objects.get_for_model(album)) #not evaluated yet

        if sort_method == 'byrating_asc' :
            result = all_reviews.order_by('rating__score')
        elif sort_method == 'byrating_desc' :
            result = all_reviews.order_by('-rating__score')
        elif sort_method == 'byscore_desc' :
            result = all_reviews.order_by('-vote_score')
        elif sort_method == 'search':
            query = request.GET['query']
            all_reviews = search_review_by_user(all_reviews, query)
            result = all_reviews.order_by('-date_last_change')
        else :
            return HttpResponseNotFound()

        nb_reviews = all_reviews.count()
        reviews_per_page = 10
        nb_pages = ceil(nb_reviews * 1.0 / reviews_per_page)
            
        sliced_result = result[((page-1)*reviews_per_page):(page*reviews_per_page)]
        response = []
        for review in sliced_result :
            response.append({
                'title' : review.title,
                'content' : review.content[:400],
                'num_up' : review.num_vote_up,
                'rating' : review.rating.score,
                'username' : review.rating.user.username,
                'url_profile' : reverse('profile', args=[review.rating.user.username]),
                'url_review' : reverse('albums:review', args=[album.mbid, review.id]),                
                })
        return JsonResponse({'data' : response, 'nbpages' : nb_pages, 'is_anonymous' : request.user.is_anonymous})

def search_review(result, query):
    words = query.split(' ')
    for word in words :
        result = result.filter(Q(rating__rating__albums__title__icontains = word) | Q(rating__rating__albums__artists__name__icontains = word))
    return result.distinct()

def user_review_list(request, username):
    if request.method == 'GET':
        sort_method = request.GET['methode']
        try : 
            page = int(request.GET['page'])
        except ValueError :
            page = 1
        if page <= 0:
            page = 1
        user = User.objects.get(username = username)
        all_reviews = Review.objects.filter(rating__user = user) #not evaluated yet

        if sort_method == 'byrating_asc' :
            result = all_reviews.order_by('rating__score')
        elif sort_method == 'byrating_desc' :
            result = all_reviews.order_by('-rating__score')
        elif sort_method == 'byscore_desc' :
            result = all_reviews.order_by('-vote_score')
        elif sort_method == 'bylastmodif':
            result = all_reviews.order_by('-date_last_change')
        elif sort_method == 'search' :
            query = request.GET['query']
            all_reviews = search_review(all_reviews, query)
            result = all_reviews.order_by('-date_last_change')
        else :
            return HttpResponseNotFound()

        nb_reviews = all_reviews.count()
        reviews_per_page = 10
        nb_pages = ceil(nb_reviews * 1.0 / reviews_per_page)
        
        sliced_result = result[((page-1)*reviews_per_page):(page*reviews_per_page)]
        response = []
        for review in sliced_result :
            album = review.rating.rating.content_object
            album_data = compute_sidebar_args(album, add_album = False)
            review_data = {
                'title' : review.title,
                'content' : review.content[:400],
                'num_up' : review.num_vote_up,
                'rating' : review.rating.score,
                'username' : review.rating.user.username,
                'url_profile' : reverse('profile', args=[review.rating.user.username]),
                'url_review' : reverse('albums:review', args=[album.mbid, review.id]),
                'url_album' : reverse('albums:album', args=[album.mbid]),
                'album_title' : album.title,
                'album_cover' : album.get_cover()
                }
            item_data = {**album_data, **review_data}
            response.append(item_data)
        return JsonResponse({'data' : response, 'nbpages' : nb_pages, 'is_anonymous' : request.user.is_anonymous, 'is_user' : (request.user == user)})
    return HttpResponseNotFound()


def search_rating(result, query):
    words = query.split(' ')
    for word in words :
        result = result.filter(Q(rating__albums__title__icontains = word) | Q(rating__albums__artists__name__icontains = word))
    return result.distinct()


def user_rating_list(request, username):
    if request.method == 'GET':
        sort_method = request.GET['methode']

        try : 
            page = int(request.GET['page'])
        except ValueError :
            page = 1
        if page <= 0:
            page = 1
        user = User.objects.get(username = username)
        all_ratings = UserRating.objects.filter(user = user) #not evaluated yet
        if sort_method == 'byrating_asc' :
            result = all_ratings.order_by('score')
        elif sort_method == 'byrating_desc' :
            result = all_ratings.order_by('-score')
        elif sort_method == 'bylastmodif':
            result = all_ratings.order_by('-modified')
        elif sort_method == 'search':
            query = request.GET['query']
            all_ratings = search_rating(all_ratings, query).order_by('-modified')
            result = all_ratings
        else :
            return HttpResponseNotFound()

        nb_ratings = all_ratings.count()
        ratings_per_page = 20
        nb_pages = ceil(nb_ratings * 1.0 / ratings_per_page)

        sliced_result = result[((page-1)*ratings_per_page):(page*ratings_per_page)]
        response = []
        for rating in sliced_result :
            album = rating.rating.content_object
            album_data = compute_sidebar_args(album, add_album = False)
            if request.user.is_authenticated :
                followees_avg = rating_for_followees(request.user, album)
                user_rating = UserRating.objects.for_instance_by_user(album, user = request.user)
                if user_rating == None:
                    user_rating = 0
                else :
                    user_rating = user_rating.score
            else :
                followees_avg = 0
                user_rating = 0
            rating_data = {
                'rating' : rating.score,
                'average' : floatformat(rating.rating.average, 1),
                'username' : rating.user.username,
                'url_profile' : reverse('profile', args=[rating.user.username]),
                'url_album' : reverse('albums:album', args=[album.mbid]),
                'album_title' : album.title,
                'album_cover' : album.get_cover(),
                'followees_avg' : floatformat(followees_avg, 1),
                'user_rating' : user_rating,
                }
            try:
                rating_data['url_review'] = reverse('albums:review', args=[album.mbid, rating.review.id])
            except Review.DoesNotExist:
                rating_data['url_review'] = None
            item_data = {**album_data, **rating_data}
            response.append(item_data)
        return JsonResponse({'data' : response, 'nbpages' : nb_pages, 'is_anonymous' : request.user.is_anonymous, 'is_user' : (request.user == user)})
    return HttpResponseNotFound()

def search_interests(result, query):
    words = query.split(' ')
    for word in words :
        result = result.filter(Q(album__title__icontains = word) | Q(album__artists__name__icontains = word))
    return result.distinct()

def user_interest_list(request, username):
    if request.method == 'GET':
        sort_method = request.GET['methode']
        
        try : 
            page = int(request.GET['page'])
        except ValueError :
            page = 1
        if page <= 0:
            page = 1
            
        user = User.objects.get(username = username)
        interests = UserInterest.objects.filter(user = user)
        if sort_method == 'search':
            query = request.GET['query']
            interests = search_interests(interests, query)
        interests = interests.order_by('-date_created')

        nb_interests = interests.count()
        interests_per_page = 20
        nb_pages = ceil(nb_interests * 1.0 / interests_per_page)

        sliced_result = interests[((page-1)*interests_per_page):(page*interests_per_page)]
        response = []
        for interest in sliced_result :
            album = interest.album
            album_data = compute_sidebar_args(album, add_album = False)
            if request.user.is_authenticated :
                followees_avg = rating_for_followees(request.user, album)
                user_rating = UserRating.objects.for_instance_by_user(album, user = request.user)
                if user_rating == None:
                    user_rating = 0
                else :
                    user_rating = user_rating.score
            else :
                followees_avg = 0
                user_rating = 0

            rating_ = UserRating.objects.for_instance_by_user(album, user=user)
            if rating_ is not None:
                rating = rating_.score
                try:
                    url_review = rating_.review.get_absolute_url()
                except Review.DoesNotExist:
                    url_review = None
            else :
                rating = 0
                url_review = None
                
            interest_data = {
                'rating' : rating,
                'average' : floatformat(album.ratings.get().average, 1),
                'username' : user.username,
                'url_profile' : user.get_absolute_url(),
                'url_album' : album.get_absolute_url(),
                'album_title' : album.title,
                'album_cover' : album.get_cover(),
                'followees_avg' : floatformat(followees_avg, 1),
                'user_rating' : user_rating,
                'url_review' : url_review
                }

            response.append({**interest_data, **album_data})
        return JsonResponse({'data' : response, 'nbpages' : nb_pages, 'is_anonymous' : request.user.is_anonymous, 'is_user' : (request.user == user)})
    return HttpResponseNotFound()



def latest_reviews(request):
    page = request.GET.get('page')
    if page is None:
        page = 1
    else:
        try:
            page = int(page)
        except ValueError:
            page = 1
    filter_ = request.GET.get('filtre')
    if filter_ == 'abonnements' and request.user.is_authenticated :
        reviews = Review.objects.filter(rating__user__followers__follower = request.user).order_by('-date_publication')
        query = 'abonnements'
    else:
        reviews = Review.objects.all().order_by('-date_publication')
        query = 'tout'
    paginate = Paginator(reviews, 10)
    try:
        list_filtered = paginate.page(page)
    except PageNotAnInteger:
        list_filtered = paginate.page(1)
    except EmptyPage:
        list_filtered = paginate.page(paginate.num_pages)
    page_list = get_page_list(paginate.num_pages, page)
    context = {
        'list' : list_filtered,
        'query' : query,
        'page' : page,
        'page_list' : page_list,
        }
    return render(request, 'ratings/latest_reviews.html', context)
    


def review_notification(user, review):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + ' a apprécié ' + "<a href='{}'>votre critique</a>".format(reverse('albums:review', args=[review.rating.rating.albums.get().mbid, review.id])) + ' sur l\'album ' + "<a href='{}'>{}</a>".format(reverse('albums:album', args=[review.rating.rating.albums.get().mbid]), review.rating.rating.albums.get().title)
    return res

@login_required
def ajax_vote(request):
    if request.method == 'POST':
        review_id = request.POST['element_id']
        review = get_object_or_404(Review, pk = review_id)
        user = User.objects.get(id = request.user.id)
        if request.POST['type'] == 'up':
            review.votes.up(user.id)
            notify.send(sender = request.user, recipient = review.rating.user, verb = "a apprécié votre critique", target = review, to_str = review_notification(request.user, review))
        elif request.POST['type'] == 'down':
            review.votes.down(user.id)
            same_notifications(review.rating.user.notifications, actor = request.user, verb = "a apprécié votre critique", target = review).delete()
        elif request.POST['type'] == 'none':
            review.votes.delete(user.id)
            same_notifications(review.rating.user.notifications, actor = request.user, verb = "a apprécié votre critique", target = review).delete()
        ups = review.num_vote_up
        downs = review.num_vote_down
    return JsonResponse({'ups' : ups, 'downs' : downs})


@login_required
def ajax_delete_rating(request):
    if request.method == 'POST' :
        mbid = request.POST.get('mbid')
        album = get_object_or_404(Album, mbid = mbid)
        user_rating = UserRating.objects.for_instance_by_user(album, user=request.user)
        if user_rating:
            user_rating.delete()
            return JsonResponse({})
    return HttpResponseNotFound()
