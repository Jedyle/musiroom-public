from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from friendship.models import Follow
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.contrib.staticfiles.templatetags.staticfiles import static
from account.utils import same_notifications
from notifications.signals import notify
# Create your views here.

def follow_notification(user):
    return "<a href={}>{}</a> ".format(reverse('profile', args=[user.username]), user.username) + "vous suit"

@login_required
def ajax_follow(request):
    if request.method == 'POST':
        follow = request.POST['follow']
        user_to_follow = User.objects.get(username = request.POST['user_to_follow'])
        user = request.user
        if follow == 'true':
            if not Follow.objects.follows(user, user_to_follow):
                print('follow')
                Follow.objects.add_follower(user, user_to_follow)
                notify.send(sender = user, recipient = user_to_follow, verb = "vous suit", to_str = follow_notification(request.user))

        elif follow == 'false':
            if Follow.objects.follows(user, user_to_follow):
                Follow.objects.remove_follower(user, user_to_follow)
                same_notifications(user_to_follow.notifications, actor=user, verb="vous suit").delete()
        return JsonResponse({})
    return HttpResponseNotFound()


def make_json_contact_list(querydict, user=None):
    contact_list = []
    for f in querydict:
        contact = {}
        contact['username'] = f.username
        contact['profile_url'] = reverse('profile', args=[f.username])
        contact['avatar'] = f.account.get_avatar()
            
        if (user is not None) and Follow.objects.follows(user, f):
            contact['follows'] = True
        elif (user is not None) :
            contact['follows'] = False
        else:
            contact['follows'] = None

        if user == f:
            contact['is_self'] = True
        else:
            contact['is_self'] = False

        contact_list.append(contact)
        
    return contact_list
    

def ajax_contacts(request, username):
    if request.method == 'GET':
        query_type = request.GET['type']
        user = User.objects.get(username = username)
        if query_type == 'abonnes':
            contacts = User.objects.filter(following__followee = user)
            print(contacts)
            
        elif query_type == 'abonnements' :
            contacts = User.objects.filter(followers__follower = user)

        elif query_type == 'tout' :
            contacts = User.objects.filter( Q(followers__follower = user) | Q(following__followee = user) ).distinct()

        sort = request.GET['tri']

        if sort == 'alphabetique':
            contacts = contacts.order_by('username')
        elif sort == 'derniere_connexion':
            contacts = contacts.order_by('-last_login')
            

        if request.user.is_authenticated:        
            contact_list = make_json_contact_list(contacts, user=request.user)
        else:
            contact_list = make_json_contact_list(contacts)

        url_follow = reverse('ajax_follower:ajax_follow')
        print(contact_list)
        return JsonResponse({ 'contacts' : contact_list , 'url_follow' : url_follow})
    return HttpResponseNotFound()


