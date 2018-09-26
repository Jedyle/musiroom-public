from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib.contenttypes.models import ContentType
from .forms import DiscussionForm, EditDiscussionForm
from .models import Discussion
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib.auth.models import User
from .settings import get_search_fields_config, DEFAULT_SEARCH_FIELD
from django.apps import apps

# Create your views here.

@login_required
def create_discussion(request, content_id=None, object_id=None):
    if content_id is None or object_id is None:
        form = DiscussionForm()
        return render(request, 'discussions/choose_object_for_creation.html', {'discussion_form' : form})
    if int(content_id) == 0 or int(object_id) == 0:
        instance = None
    else:
        content_type = ContentType.objects.get(pk = content_id)
        ct_class = content_type.model_class()
        instance = ct_class.objects.get(pk = object_id)
        
    if request.method == 'POST' : 
        form = DiscussionForm(instance, request.POST)
        if form.is_valid():
            discussion = form.get_discussion_object()
            discussion.author = request.user
            discussion.save()
            return redirect(discussion.get_absolute_url())
        else :
            context = {
                'discussion_form' : form,
                'target_object' : instance,
                'target_object_ct' : content_id,
                'target_object_pk' : object_id,
                }
            return render(request, 'discussions/create.html', context)
    else :
        context = {
            'discussion_form' : DiscussionForm(target_object = instance),
            'target_object' : instance,
            'target_object_ct' : content_id,
            'target_object_pk' : object_id,
            }
        return render(request, 'discussions/create.html', context)
    

def display_discussion(request, id):
    discussion = get_object_or_404(Discussion, pk = id)
    context = {
        'discussion' : discussion,
        }
    return render(request, 'discussions/display.html', context) 


@login_required
def edit_discussion(request, id):
    discussion = get_object_or_404(Discussion, pk = id)
    if discussion.author != request.user:
        return HttpResponseForbidden()    
    if request.method == 'POST':
        discussion_form = EditDiscussionForm(request.POST, instance = discussion)
        if discussion_form.is_valid():
            discussion_form.save()
            return redirect(discussion.get_absolute_url())
        else:
            context = {
                'discussion_form' : discussion_form,
                'errors' : True,
                'discussion' : discussion,
                }
            return render(request, 'discussions/edit.html', context)
    else:
        discussion_form = EditDiscussionForm(instance = discussion)
        context = {
            'discussion_form' : discussion_form,
            'errors' : False,
            'discussion' : discussion,
            }
        return render(request, 'discussions/edit.html', context)
        
@login_required        
def confirm_delete(request, id):
    discussion = get_object_or_404(Discussion, pk=id)
    if discussion.author != request.user:
        return HttpResponseForbidden()
    context = {
        'discussion' : discussion
        }
    return render(request, 'discussions/confirm_delete.html', context)

@login_required
def delete_discussion(request, id):
    discussion = get_object_or_404(Discussion, pk=id)
    if discussion.author != request.user:
        return HttpResponseForbidden()
    content_object = discussion.content_object
    discussion.delete()
    """
    Modifier redirect quand on aura les listes de discussions
    """
    return redirect(reverse('discussions:search_discussion_for_object', args=[ContentType.objects.get_for_model(content_object).pk, content_object.pk]))

def search_discussion_for_object(request, content_id=None, object_id=None):
    author = request.GET.get('auteur')
    title = request.GET.get('titre')
    page = request.GET.get('page')
    query = request.GET.get('filtre')
    
    if not page :
        page = 1
    discussions = Discussion.objects.all()
    if content_id is not None and object_id is not None:
        if int(content_id) == 0 or int(object_id) == 0: #general discussion
            discussions = discussions.filter(content_type = None)
            instance = 0
        else :
            content_type = ContentType.objects.get(pk = content_id)
            ct_class = content_type.model_class()
            instance = ct_class.objects.get(pk = object_id)
            discussions = discussions.filter(content_type = content_type, object_id = object_id)
    else:
        instance = None
        
    if author:
        discussions = discussions.filter(author__username__icontains = author)
    if title:
        discussions = discussions.filter(title__icontains = title)
        
    if query == 'meilleurs' :
        discussions = discussions.order_by('-vote_score')
    elif query == 'récents' :
        pass #trié par défaut
    elif query == 'populaires' :
        discussions = discussions.filter(vote_score__gt = 3)

    """
    Quand le site sera devenu populaire, penser à ajouter un filtre 'aujourdhui, cette semaine, ce mois...'
    """

    paginator = Paginator(discussions, 20)
    try:
        discussions_filtered = paginator.page(page)
    except PageNotAnInteger:
        discussions_filtered = paginator.page(1)
    except EmptyPage:
        discussions_filtered = paginator.page(paginator.num_pages)
                                            
    context = {
        'discussions' : discussions_filtered,
        'instance' : instance,
        'paginate' : paginator.num_pages > 1,
        'author' : author,
        'title' : title,
        'query' : query,
        'page' : page,
        }
    return render(request, 'discussions/search_discussion_for_object.html', context)     


@login_required
def ajax_vote(request):
    if request.method == 'POST':
        pk = request.POST.get('id')
        discussion = get_object_or_404(Discussion, pk = pk)
        user = User.objects.get(id = request.user.id)
        if request.POST['type'] == 'up':
            discussion.votes.up(user.id)
        elif request.POST['type'] == 'down':
            discussion.votes.down(user.id)
        elif request.POST['type'] == 'none':
            discussion.votes.delete(user.id)
        ups = discussion.num_vote_up
        downs = discussion.num_vote_down
        return JsonResponse({'ups' : ups, 'downs' : downs})
    return HttpResponseForbidden()

@login_required
def ajax_search_object(request):
    query = request.GET.get('query')
    o_type = request.GET.get('model')

    search_conf = get_search_fields_config()
    model_search_field = search_conf.get(o_type, DEFAULT_SEARCH_FIELD)

    ct = ContentType.objects.get(model = o_type.lower())
    Model = ct.model_class()

    res = Model.objects.filter(**{ model_search_field + '__icontains' : query })[:10]

    json_result = []
    for item in res:
        json_result.append({
            'name' : str(item),
            'url' : reverse('discussions:create_discussion', args=[ct.pk, item.pk]),
            })
    return JsonResponse(json_result, safe=False)


def ajax_get_discussions_for_user(request):
    if request.method == 'GET':
        username = request.GET['username']
        discussions = Discussion.objects.filter(author__username = username)
        discs = []
        for disc_elt in discussions:
            discs.append({
                'title' : disc_elt.title,
                'link' : disc_elt.get_absolute_url(),
                'disc_id' : disc_elt.id,
                'content_object' : str(disc_elt.content_object),
                'content_object_url' : disc_elt.content_object.get_absolute_url(),
                })
        return JsonResponse({'discussions' : discs})
    return HttpResponseNotFound()  
