from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse, HttpResponseNotFound, QueryDict
from django.contrib.auth.models import User
from .models import ItemList, ListObject
from .forms import ItemListForm
from star_ratings.models import Rating, UserRating
from albums.utils import compute_artists_links
from django.contrib.auth.decorators import login_required
from albums.models import Album
from ratings.utils import rating_for_followees
from math import ceil
from django.template.defaultfilters import floatformat
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q, F
from notifications.signals import notify
from account.utils import same_notifications

# Create your views here.

ITEMS_PER_PAGE = 10

def get_vote(l_list, user):
    if (l_list.votes.exists(user.id, action = 0)): #up
        return "up"
    elif (l_list.votes.exists(user.id, action = 1)): #down
        return "down"
    else:
        return "none"

def display_list(request, list_id):
    itemlist = ItemList.objects.get(pk = list_id)
    items = ListObject.objects.filter(item_list = itemlist).prefetch_related('album__artists')
    author = itemlist.user
    res_items = []
    for item in items[:ITEMS_PER_PAGE]:
        album = item.album
        rating = Rating.objects.for_instance(album)
        if request.user.is_authenticated:
            user_rating = UserRating.objects.for_instance_by_user(album, user = request.user)
            followees_rating = rating_for_followees(request.user, album)
        else:
            user_rating = 0
            followees_rating = 0
        author_rating = UserRating.objects.for_instance_by_user(album, user = author)

        
        res_item = {
            'album' : album,
            'rank' : item.order,
            'comment' : item.comment,
            'author_rating' : author_rating,
            'user_rating' : user_rating,
            'average_rating' : floatformat(rating.average, 1),
            'artists' : compute_artists_links(album),
            'old_comment' : '',
            'mbid' : album.mbid,
            'followees_rating' : floatformat(followees_rating, 1),
            }
        res_items.append(res_item)

    if request.user.is_authenticated :
        user_vote = get_vote(itemlist, request.user)
    else :
        user_vote = "none"


    context = {
        'list' : res_items,
        'infos' : itemlist,
        'nb_pages' : ceil(items.count() * 1.0 / ITEMS_PER_PAGE),
        'list_url' : reverse('lists:ajax_list'),
        'edit_description_url' : reverse('lists:ajax_set_description'),
        'get_items_url' : reverse('lists:ajax_get_items'),
        'can_edit' : (request.user == itemlist.user),
        'move_item_url' : reverse('lists:ajax_move_items'),
        'search_url' : reverse('albums:ajax_search_in_db'),
        'edit_url' : reverse('lists:ajax_set_item'),
        'delete_url' : reverse('lists:ajax_delete_item'),
        'delete_list_url' : reverse('lists:ajax_delete_list'),
        'user_vote' : user_vote,
        }
    return render(request, 'lists/list.html', context)

def search_list_in_db(query, sort, page):
    words = query.split(' ')
    list_list = ItemList.objects.all()
    for word in words:
        list_list = list_list.filter( Q(title__icontains = word) | Q(user__username__icontains = word) )

    if sort == 'score':
        list_list = list_list.order_by('-vote_score')
    elif sort == 'votes':
        list_list = list_list.annotate(nb_votes = F('num_vote_up') + F('num_vote_down')).order_by('-nb_votes')
    
    paginator = Paginator(list_list, 10)
    try:
        list_filtered = paginator.page(page)
    except PageNotAnInteger:
        list_filtered = paginator.page(1)
    except EmptyPage:
        list_filtered = paginator.page(paginator.num_pages)
    return list_filtered

def search_list(request):
    m_type = request.GET.get('type')
    query = request.GET.get('query')
    page = request.GET.get('page')
    tri = request.GET.get('tri')
    if not query or (m_type != 'liste') :
        return redirect('/')
    else :
        if not page :
            page = 1
        if not tri:
            tri = ''
        list_list = search_list_in_db(query, tri, page)
        context = {
            'lists' : list_list,
            'paginate' : True,
            'query' : query,
            'tri' : tri,
            'm_type' : m_type,
            'page' : page,
            }
        return render(request, 'lists/search_list.html', context)            
                

def ajax_list(request):
    if request.method == 'GET':
        list_id = int(request.GET['list_id'])
        page = int(request.GET['page'])
        itemlist = ItemList.objects.get(pk = list_id)
        items = ListObject.objects.filter(item_list = itemlist).prefetch_related('album__artists')
        author = itemlist.user
        nb_items = items.count()
        nb_pages = ceil(nb_items * 1.0 / ITEMS_PER_PAGE)
        result = items[((page-1)*ITEMS_PER_PAGE):(page*ITEMS_PER_PAGE)]
        res_items = []
        for item in result:
            album = item.album
            rating = Rating.objects.for_instance(album)

            if request.user.is_authenticated:
                user_rating = UserRating.objects.for_instance_by_user(album, user = request.user)
                if user_rating:
                    user_rating = user_rating.score
                else :
                    user_rating = 0
                followees_rating = rating_for_followees(request.user, album)
            else:
                user_rating = 0
                followees_rating = 0
            author_rating = UserRating.objects.for_instance_by_user(album, user = author)
            if author_rating:
                author_rating = author_rating.score
            else :
                author_rating = 0
            res_item = {
                'title' : album.title,
                'cover' : album.get_cover(),
                'artists' : compute_artists_links(album),
                'rank' : item.order,
                'album_url' : reverse('albums:album', args=[album.mbid]),
                'avg_rating' : floatformat(rating.average, 1),
                'author_rating' : author_rating,
                'user_rating' : user_rating,
                'comment' : item.comment,
                'editable' : False,
                'old_comment' : "",
                'mbid' : album.mbid,
                'followees_rating' : floatformat(followees_rating, 1),
                }
            res_items.append(res_item)
        return JsonResponse({'list' : res_items, 'nb_pages' : nb_pages})
    return HttpResponseNotFound()
            

@login_required
def create_list(request):
    if request.method == 'POST':
        itemlist = ItemListForm(request.POST)
        if itemlist.is_valid():
            model_list = itemlist.save(commit=False) 
            model_list.user = request.user
            model_list.save()
            return redirect('lists:display_list', list_id = model_list.id)
        else:
            return render(request, 'list/create.html', {'form' : itemlist})
    else:
        form = ItemListForm(user = request.user)
        return render(request, 'lists/create.html', {'form' : form})

@login_required
def ajax_set_description(request):
    if request.method == 'POST':
        list_id = int(request.POST['list_id'])
        description = request.POST['description']
        itemlist = ItemList.objects.get(pk = list_id)
        if itemlist.user == request.user:
            itemlist.description = description
            itemlist.save()
            return JsonResponse({})
    return HttpResponseNotFound()

@login_required
def ajax_delete_item(request):
    if request.method == 'POST':
        mbid = request.POST['mbid']
        list_id = int(request.POST['list_id'])
        itemlist = get_object_or_404(ItemList, pk = list_id)
        if itemlist.user == request.user:
            try: 
                album = Album.objects.get(mbid = mbid)
                item = ListObject.objects.get(album = album, item_list = itemlist)
                item.delete()
            except (Album.DoesNotExist, ListObject.DoesNotExist):
                pass
            return JsonResponse({})
    return HttpResponseNotFound()

    

def ajax_get_items(request):
    if request.method == 'GET':
        list_id = int(request.GET['list_id'])
        itemlist = ItemList.objects.get(pk = list_id)
        items = ListObject.objects.filter(item_list = itemlist).values('order', 'album__title', 'album__mbid')
        items_json = []
        for item in items:
            items_json.append({
                'order' : item['order'],
                'title' : item['album__title'],
                'mbid' : item['album__mbid'],
                })
        return JsonResponse({'items' : items_json})
    return HttpResponseNotFound()

@login_required
def ajax_move_items(request):
    if request.method == 'POST':
        list_id = int(request.POST['list_id'])
        itemlist = ItemList.objects.get(pk = list_id)
        if itemlist.user == request.user : 
            item_id = int(request.POST['item'])
            destination_id = int(request.POST['destination'])
            items = ListObject.objects.filter(item_list = itemlist)
            item = ListObject.objects.get(item_list = itemlist, order = item_id)
            nb_items = items.count()
            if destination_id <= nb_items and item_id <= nb_items and item_id >=1 and destination_id >= 1 :
                if destination_id < item_id:
                    for elt in items[destination_id-1:item_id-1]:
                        elt.order+=1
                        elt.save()
                    item.order = destination_id
                    item.save()
                elif destination_id > item_id:
                    for elt in items[item_id:destination_id]:
                        elt.order-=1
                        elt.save()
                    item.order = destination_id
                    item.save()
                items = ListObject.objects.filter(item_list = itemlist)
                return JsonResponse({})
    return HttpResponseNotFound()

@login_required
def ajax_set_item(request):
    if request.method == 'POST':
        list_id = int(request.POST['list_id'])
        itemlist = ItemList.objects.get(pk = list_id)
        if itemlist.user == request.user:
            mbid = request.POST['mbid']
            comment = request.POST['comment']
            album = Album.objects.get(mbid = mbid)
            item, created = ListObject.objects.get_or_create(item_list = itemlist, album=album)
            item.comment = comment
            item.save()
            return JsonResponse({'created' : created})
    return HttpResponseNotFound()

@login_required
def ajax_delete_list(request):
    if request.method == 'POST':
        list_id = int(request.POST['list_id'])
        itemlist = get_object_or_404(ItemList, pk = list_id)
        if itemlist.user == request.user :
            itemlist.delete()
            return JsonResponse({})
    return HttpResponseNotFound()

@login_required
def get_lists_for_user_and_album(request):
    if request.method == 'GET' :
        itemlists = ItemList.objects.filter(user = request.user)
        mbid = request.GET['mbid']
        album = get_object_or_404(Album, mbid = mbid)
        lists_contains_alb = []
        lists_doesnt_contain_alb = []
        for list_elt in itemlists:
            list_item = {
                'list_id' : list_elt.id,
                'title' : list_elt.title,
                }
            try: 
                list_obj = ListObject.objects.get(album = album, item_list = list_elt)
                list_item['comment'] = list_obj.comment
                list_item['is_in_list'] = True
                lists_contains_alb.append(list_item)
            except ListObject.DoesNotExist:
                list_item['comment'] = ''
                list_item['is_in_list'] = False
                lists_doesnt_contain_alb.append(list_item)
        lists_contains_alb.extend(lists_doesnt_contain_alb)
        lists = lists_contains_alb
        return JsonResponse({'lists' : lists})
    return HttpResponseNotFound({})
                 

def ajax_get_lists_for_user(request):
    if request.method == 'GET':
        username = request.GET['username']
        itemlists = ItemList.objects.filter(user__username = username)
        lists = []
        for list_elt in itemlists:
            lists.append({
                'title' : list_elt.title,
                'link' : reverse('lists:display_list', args=[list_elt.id]),
                'list_id' : list_elt.id,
                'nb_items' : list_elt.albums.count(),
                })
        return JsonResponse({'lists' : lists})
    return HttpResponseNotFound()            

def list_notification(user, list):
    res = "<a href='{}'>{}</a>".format(reverse('profile', args=[user.username]),user.username) + ' a apprécié votre liste ' + "<a href='{}'>{}</a>".format(reverse('lists:display_list', args=[list.id]), list.title)
    return res

@login_required
def ajax_vote(request):
    if request.method == 'POST':
        list_id = request.POST.get('element_id')
        list_item = get_object_or_404(ItemList, pk = list_id)
        user = request.user
        if request.POST['type'] == 'up':
            list_item.votes.up(user.id)
            notify.send(sender = request.user, recipient = list_item.user, verb = "a apprécié votre liste", target = list_item, to_str = list_notification(request.user, list_item))
        elif request.POST['type'] == 'down':
            list_item.votes.down(user.id)
            same_notifications(list_item.user.notifications, actor = request.user, verb = "a apprécié votre liste", target = list_item).delete()
        elif request.POST['type'] == 'none':
            list_item.votes.delete(user.id)
            same_notifications(list_item.user.notifications, actor = request.user, verb = "a apprécié votre liste", target = list_item).delete()
        ups = list_item.num_vote_up
        downs = list_item.num_vote_down
    return JsonResponse({'ups' : ups, 'downs' : downs})
