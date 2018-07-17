from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Count, Q, Avg
from django.urls import reverse
from .scraper import ParseAlbum, ParseArtist, ParseArtistPhoto, ParseCover, ParseSearchArtists, ParseSearchAlbums, get_page_list
from .models import Album, Artist, Genre, AlbumGenre
from ratings.models import Review
from ratings.utils import rating_for_followees, rating_for_followees_list
from star_ratings.models import Rating, UserRating
from .forms import GenreForm, AlbumGenreForm
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from .utils import compute_artists_links
from lists.views import search_list
from lists.models import ItemList
import re
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType

# Create your views here.

def get_artists_in_db(artist_dict):
    artists = []
    for artist_elt in artist_dict:
        try:
            artist = Artist.objects.get(mbid = artist_elt['mbid'])
            artists.append(artist)
        except Artist.DoesNotExist:
            artist = Artist.objects.create(mbid = artist_elt['mbid'], name = artist_elt['name'])
            artists.append(artist)
    return artists

def search_in_db(query, page, items_per_page):
    words = query.split(' ')
    albums = Album.objects
    for word in words:
        albums = albums.filter( Q(title__icontains = word) | Q(artists__name__icontains = word) )
    return albums.distinct()[(page-1)*items_per_page: page*items_per_page]


def compute_sidebar_args(album, add_album = True):
    album_genres = AlbumGenre.objects.filter(Q(album = album) & Q(is_genre=True)).order_by('-vote_score').select_related('genre')
    genre_names = ["<a href='{}'>{}</a>".format(reverse('albums:genre', args=[album_genre.genre.slug]), album_genre.genre.name) for album_genre in album_genres]
    context = {
        'artists' : compute_artists_links(album),
        'genres': ", ".join(genre_names),
        'mbid' : album.mbid,
        }
    if add_album == True:
        context['album'] = album
    return context

def all_followees_ratings(user, album):
    ratings = UserRating.objects.filter(Q(rating__albums = album) & Q(user__followers__follower = user))
    res = []
    count = [0 for i in range(10)]
    for rating in ratings :
        try: 
            review_id = rating.review.id
        except Review.DoesNotExist:
            review_id = None
        res.append({
            'user' : rating.user,
            'score' : rating.score,
            'review_id' : review_id,
            })
        count[rating.score-1]+=1
    return {
        'ratings' : res,
        'chart' : count,
        'avg' : ratings.aggregate(avg = Avg('score'))['avg'] or 0,
        }

NB_LISTS = 10

def album(request, mbid):
    try:
        album = Album.objects.get(mbid = mbid)
        context = compute_sidebar_args(album)
        lists = ItemList.objects.filter(albums = album).exclude(title__contains = "Top Albums de").order_by('-vote_score').select_related('user')[:NB_LISTS]
        context['lists'] = lists
        same_artist = Album.objects.filter(artists__in = album.artists.all()).exclude(pk = album.pk).filter(ratings__isnull = False).order_by('-ratings__count')[:3]
        context['same_artist'] = same_artist
        try:
            context['average'] = album.ratings.get().average
        except Rating.DoesNotExist:
            context['average'] = 0
        if not request.user.is_anonymous:
            user_rating = UserRating.objects.for_instance_by_user(album, user=request.user)
            rated = user_rating is not None
            if rated:
                try:
                    review = user_rating.review
                except Review.DoesNotExist:
                    review = None
            else:
                review = False
            context['rated'] = rated
            context['review'] = review
            followees_ratings = all_followees_ratings(request.user, album)
            context['followees_avg'] = followees_ratings['avg']
            context['followees_ratings'] = followees_ratings['ratings'] 
        return render(request, 'albums/album.html', context)
    except Album.DoesNotExist:
        parser = ParseAlbum(mbid)
        if not parser.load():
            return HttpResponseNotFound()
        else:
            parse_cover = ParseCover(mbid)
            if parse_cover.load():
                cover_url = parse_cover.get_cover_small()
            else:
                cover_url = ""
            album = Album.objects.create(mbid = mbid, title = parser.get_title(), release_date=parser.get_release_date(), cover = cover_url, album_type = parser.get_type())
            authors = get_artists_in_db(parser.get_artists())
            for author in authors :
                album.artists.add(author)
            album.save()
            artists = [{'name' : author.name, 'mbid' : author.mbid} for author in authors]
            artists_links = ["<a href='{}'>{}</a>".format(reverse('albums:artist', args=[artist['mbid']]), artist['name']) for artist in artists]
            context = {
                'album' : album,
                'artists' : ', '.join(artists_links),
                'mbid': mbid,
                }
            return render(request, 'albums/album.html', context)

def browse_albums(request):
    albums = Album.objects.all()
    try:
        page = request.GET.get('page')
        if page is None:
            page = 1
        else:
            page = int(page)
    except ValueError:
        page = 1
    year = request.GET.get('annee')
    slug = request.GET.get('genre')
    query = request.GET.get('recherche')
    if year and year != "tout":
        m = re.match(r'^([0-9]{4})s$', year)
        if m is not None:
            decade = int(m.group(1))
            years = [(decade + i) for i in range(10)]
            albums = albums.filter(release_date__year__in = years)
        else:
            try:
                year = int(year)
                albums = albums.filter(release_date__year = year)
            except ValueError:
                year = "tout"
    else:
        year = "tout"

    if slug and slug != "tout":
        albums = albums.filter(Q(albumgenre__genre__slug = slug) & Q(albumgenre__is_genre = True))
    else :
        slug = "tout"

    if query:
        words = query.split(' ')
        for word in words:
            albums = albums.filter(Q(title__icontains = word) | Q(artists__name__icontains = word))
    else:
        query = ''
    albums = albums.filter(Q(ratings__isnull=False)).distinct().prefetch_related('artists').order_by('-ratings__average')
    paginate = Paginator(albums, 30)
    try:
        albums_filtered = paginate.page(page)
    except PageNotAnInteger:
        albums_filtered = paginate.page(1)
    except EmptyPage:
        albums_filtered = paginate.page(paginate.num_pages)

    if request.user.is_authenticated :
        user_ratings = UserRating.objects.for_instance_list_by_user(albums_filtered.object_list, request.user)
        followees_ratings = rating_for_followees_list(request.user, albums_filtered.object_list)
    
    itemlist = []
    for i,album in enumerate(albums_filtered):
        item = {
            'album' : album,
            'artists' : compute_artists_links(album),
            }
        if request.user.is_authenticated :
            item['user_rating'] = user_ratings[i]
            item['followees_rating'] = followees_ratings.get(album.mbid, 0)
        itemlist.append(item)
    genres_parents = Genre.objects.filter(parent__isnull = True)
    genres_children = Genre.objects.filter(parent__isnull = False).order_by('parent')

    if page > paginate.num_pages:
        page = paginate.num_pages
    elif page < 1:
        page = 1
    page_list = get_page_list(paginate.num_pages, page)
    
    context = {
        'list' : itemlist,
        'genres_parents' : genres_parents,
        'genres_children' : genres_children,
        'current_slug' : slug,
        'selected_year' : year,
        'page_list' : page_list,
        'page' : page,
        'slug' : slug,
        'year' : year,
        'query' : query,
        }
    return render(request, 'albums/browse.html', context)
    

def get_vote(album_genre, user):
    if (album_genre.votes.exists(user.id, action = 0)): #up
        return "up"
    elif (album_genre.votes.exists(user.id, action = 1)): #down
        return "down"
    else:
        return "none"


@login_required
@transaction.atomic
def album_genres(request, mbid):
    album = get_object_or_404(Album, mbid = mbid)
    genres = album.genres.all()
    user = User.objects.get(id = request.user.id)
    album_genres = AlbumGenre.objects.filter(album = album).order_by('-vote_score')
    album_genres_user = [{"gen": album_genre,"vote": get_vote(album_genre, user)} for album_genre in album_genres]
    context = compute_sidebar_args(album)
    context['genres'] = False
    all_genres = Genre.objects.all()
    all_genres_names = [genre.name for genre in all_genres]
    if request.method == 'POST' :
        add_genre_form = AlbumGenreForm(request.POST, data_list = all_genres_names)
        if add_genre_form.is_valid():
            try:
                genre = Genre.objects.get(name = add_genre_form.cleaned_data['genre_list'])
                added_album_genre = AlbumGenre.objects.get_or_create(genre = genre, album = album)[0]
                print(added_album_genre.user)
                if added_album_genre.user == None:
                    added_album_genre.user = user
                    added_album_genre.save()
                    added_album_genre.votes.up(user.id)
                return redirect('albums:album_genres', mbid=mbid)
            except Genre.DoesNotExist:
                add_genre_form.add_error('genre_list', "Ce genre n'existe pas")
    else:
        add_genre_form = AlbumGenreForm(data_list = all_genres_names)

    context['album_title'] = album.title
    context['genre_form'] = add_genre_form
    context['album_genres_user'] = album_genres_user
    return render(request, 'albums/album_genres.html', context)

def artist(request, mbid):
    try:
        page = request.GET.get('page')
        if page is not None:
            page = int(page)
        else:
            page = 1
    except ValueError:
        page = 1
    search = request.GET.get('nom')
    if search is None:
        search = ""
    context = {
        'page' : page,
        'search' : search,
        'mbid' : mbid,
        }
    try:
        artist = Artist.objects.get(mbid = mbid)
        artist_genres = AlbumGenre.objects.filter(album__artists__in = [artist], vote_score__gt = 0).values('genre__name', 'genre__slug').annotate(total = Count('genre')).order_by('-total')[:5]
        artist_genres = ["<a href='{}'>{}</a>".format(reverse('albums:genre', args=[artist_genre['genre__slug']]), artist_genre['genre__name']) for artist_genre in artist_genres]
        genres = ", ".join(artist_genres)
        context['artist_name'] = artist.name
        context['genres'] = genres
    except Artist.DoesNotExist:
        pass
    parserphoto = ParseArtistPhoto(mbid)
    if parserphoto.load():
        picture = parserphoto.get_thumb()
    else:
        parser = ParseArtist(mbid, page=page, name=search)
        if not parser.load():
            return HttpResponseNotFound()
        else:
            picture = ""
    context['artist_picture'] = picture
    return render(request, 'albums/artist.html', context)

def ajax_artist(request, mbid):
    try:
        page = request.GET.get('page')
        if page is not None:
            page = int(page)
        else:
            page = 1
    except ValueError:
        page = 1
    search = request.GET.get('nom')
    if search is None:
        search = ""
    parser = ParseArtist(mbid, page=page, name=search)
    if not parser.load():
        return HttpResponseNotFound()
    else:
        artist_name = parser.get_name()
        discog = parser.get_discography()
        nb_pages = parser.get_nb_pages()
        if page > nb_pages:
            page = nb_pages
        elif page < 1:
            page = 1
        page_list = get_page_list(nb_pages, page)
    context = {
        'albums' : discog,
        'artist_name' : artist_name,
        'page_list' : page_list,
        'page' : page,
        'search' : search,
        'path' : reverse('albums:artist', args=[mbid]),
        }
    html = render_to_string('albums/ajax_artist.html', context)
    return HttpResponse(html)


def search(request):
    query = request.GET.get('query')
    m_type = request.GET.get('type')
    page = request.GET.get('page')
    if not query or not m_type:
        return redirect('/')
    else:
        if not page:
            page = 1
        else :
            try:
                page = int(page)
            except ValueError:
                page = 1
        if m_type == 'album':
            parser = ParseSearchAlbums(query, page = page)
            if parser.load():
                results = parser.get_results()
                nb_pages = parser.get_nb_pages()
                page_list = get_page_list(nb_pages, page)
                return render(request, 'albums/album_results.html', {'query' : query, 'm_type' : m_type, 'page_list' : page_list, 'page' : page, 'albums': results})
            else:
                return HttpResponseNotFound()
        elif m_type == 'artiste':
            parser = ParseSearchArtists(query, page = page)
            if parser.load():
                results = parser.get_results()
                nb_pages = parser.get_nb_pages()
                page_list = get_page_list(nb_pages, page)
                return render(request, 'albums/artist_results.html', {'query': query, 'm_type' : m_type, 'page_list' : page_list, 'page' : page, 'artists' : results})
        elif m_type == 'liste':
            return search_list(request)
        else :
            return HttpResponseNotFound()


def genre(request, slug):
    gen = get_object_or_404(Genre, slug=slug)
    children = gen.children
    top_10 = Album.objects.filter(Q(albumgenre__genre__slug = slug) & Q(albumgenre__is_genre = True) & Q(ratings__isnull=False) & Q(ratings__average__gt = 1.0) & Q(ratings__count__gt = 2)).order_by('-ratings__average')[:10]
    context = {
        'genre' : gen,
        'children' : children,
        'top' : top_10,
        }
    return render(request, 'albums/genre.html', context)


def genres(request):
    general_genres = Genre.objects.filter(parent__isnull=True)
    context = {
        'genres' : general_genres,
        }
    return render(request, 'albums/genres.html', context)

def top_album_get(request):
    slug = request.GET.get('genre')
    year = request.GET.get('annee')
    if not slug:
        slug = "tout"
    if not year:
        year = "tout"
    return redirect('albums:top_album', slug=slug, year=year)

def top_album(request, slug, year):
    albums = Album.objects.all()

    if year and year != "tout":
        m = re.match(r'^([0-9]{4})s$', year)
        if m is not None:
            decade = int(m.group(1))
            years = [(decade + i) for i in range(10)]
            albums = albums.filter(release_date__year__in = years)
        else:
            try:
                year = int(year)
                albums = albums.filter(release_date__year = year)
            except ValueError:
                year = "tout"
    if slug and slug != "tout":
        albums = albums.filter(Q(albumgenre__genre__slug = slug) & Q(albumgenre__is_genre = True))
    albums = albums.filter(Q(ratings__isnull=False) & Q(ratings__average__gt = 1.0) & Q(ratings__count__gt = 2)).order_by('-ratings__average')

    cache_albums = cache.get('top_album_albums_{}_{}'.format(slug, year))
    if cache_albums is None:
        albums = albums.prefetch_related('artists')[:100]
        cache.set('top_album_albums_{}_{}'.format(slug, year), albums)
    else:
        albums = cache_albums

    ratings = list(albums.values('ratings__average'))
        
    if request.user.is_authenticated :
        user_ratings = UserRating.objects.for_instance_list_by_user(albums, request.user)
        followees_ratings = rating_for_followees_list(request.user, albums)
        
    itemlist = []            
    for i,album in enumerate(albums):
        item = {
            'album' : album,
            'artists' : compute_artists_links(album),
            'avg_rating' : ratings[i]
            }
        if request.user.is_authenticated :
            item['user_rating'] = user_ratings[i]
            item['followees_rating'] = followees_ratings.get(album.mbid, 0)
        itemlist.append(item)
    genres_parents = Genre.objects.filter(parent__isnull = True)
    genres_children = Genre.objects.filter(parent__isnull = False).order_by('parent')
    
    context = {
        'list' : itemlist,
        'genres_parents' : genres_parents,
        'genres_children' : genres_children,
        'current_slug' : slug,
        'selected_year' : year,
        }
    return render(request, 'albums/top.html', context)

@login_required
def ajax_vote(request):
    if request.method == 'POST':
        mbid = request.POST.get('mbid')
        slug = request.POST.get('slug')
        genre = get_object_or_404(Genre, slug = slug)
        album = get_object_or_404(Album, mbid = mbid)
        album_genre = get_object_or_404(AlbumGenre, album = album, genre = genre)
        user = User.objects.get(id = request.user.id)
        if request.POST['type'] == 'up':
            album_genre.votes.up(user.id)
        elif request.POST['type'] == 'down':
            album_genre.votes.down(user.id)
        elif request.POST['type'] == 'none':
            album_genre.votes.delete(user.id)
        ups = album_genre.num_vote_up
        downs = album_genre.num_vote_down
    return JsonResponse({'ups' : ups, 'downs' : downs})

def album_lists(request, mbid):
    page = request.GET.get('page')
    album = get_object_or_404(Album, mbid = mbid)
    lists = ItemList.objects.filter(albums = album).order_by('-vote_score')
    paginate = Paginator(lists, 20)
    try:
        list_filtered = paginate.page(page)
    except PageNotAnInteger:
        list_filtered = paginate.page(1)
    except EmptyPage:
        list_filtered = paginate.page(paginate.num_pages)
    context = {
        'lists' : list_filtered,
        'album' : album,
        'artists' : compute_artists_links(album),
        'paginate' : (paginate.num_pages > 1),
        }
    return render(request, 'albums/album_lists.html', context)
    

@login_required
def report_genre(request):
    if request.method == 'POST':
        mbid = request.POST.get('mbid')
        slug = request.POST.get('slug')
        genre = get_object_or_404(Genre, slug = slug)
        album = get_object_or_404(Album, mbid = mbid)
        album_genre = get_object_or_404(AlbumGenre, album = album, genre = genre)
        album_genre.set_flag(request.user, status=AlbumGenre.FLAG_SPAM)
    return JsonResponse({})

@login_required
@transaction.atomic
def submit_genre(request):
    context = {}
    if request.method == 'POST':
        genre_form = GenreForm(request.POST)        
        if genre_form.is_valid():
            genre_form.save()
            return render(request, 'albums/genre_submission_complete.html')
        else:
            context['genre_form']= genre_form
            return render(request, 'albums/submit_genre.html', context)
    else:
        context['genre_form'] = GenreForm()
    return render(request, 'albums/submit_genre.html', context)


def ajax_search_in_db(request):
    if request.method == 'GET':
        query = request.GET['query']
        page = int(request.GET['page'])
        items_per_page = int(request.GET['items_per_page'])
        albums = search_in_db(query, page, items_per_page)
        albums_list = []
        for album in albums :
            albums_list.append({
                'title' : album.title,
                'mbid' : album.mbid,
                'cover' : album.get_cover(),
                'artists' : [{
                              'name' : artist.name,
                               'mbid' : artist.mbid,
                               'url' : reverse('albums:artist', args=[artist.mbid]),
                                } for artist in album.artists.all()],
                })
        return JsonResponse({'albums' : albums_list})
    return HttpResponseNotFound()
