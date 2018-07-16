from django.template.loader import render_to_string
from django.shortcuts import render, get_object_or_404, render_to_response, redirect

from .models import Account
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .forms import RegistrationForm, EditUserForm, EditAccountForm, PasswordConfirmForm
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.auth.decorators import login_required
from friendship.models import Follow
from star_ratings.models import UserRating
from ratings.models import Review
from ratings.charts import UserRatingsBarChart
from lists.models import ItemList
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

@transaction.atomic
def register(request):
    if request.user.is_authenticated :
        return redirect('/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            addr = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username=username, password=password, email=addr, is_active=False)
            profil = Account(user = user)
            top_albums = ItemList(user = user, title = "Top Albums de " + user.username, ordered = True)
            top_albums.save()
            profil.top_albums = top_albums
            profil.save()
            current_site = get_current_site(request)
            mail_subject = 'Activez votre compte.'
            message = render_to_string('account/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token':account_activation_token.make_token(user),
            })
            to_email = addr
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request, 'account/confirm_email.html', {'email': addr})
        else:
            return render(request, 'account/registration_form.html',{'form': form})
    else:
        return render(request, 'account/registration_form.html',{'form': RegistrationForm()})

def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('registration_complete')
    else:
        return HttpResponse('Lien d\'activation invalide ou expiré.')

def registration_complete(request):
    return render(request, 'account/registration_complete.html')

@login_required
def loggedin(request):
    return render(request, 'account/loggedin.html')

def profile(request, username):
    user = get_object_or_404(User, username = username)
    profile = user.account
    if request.user.is_authenticated:
        is_followed = Follow.objects.follows(user, request.user)
        follows = Follow.objects.follows(request.user, user)
    else:
        is_followed = None
        follows = None
    context = {
        'profile': profile,
        'is_followed' : is_followed,
        'follows' : follows,
        'nb_reviews' : Review.objects.filter(rating__user = user).count(),
        'nb_ratings' : UserRating.objects.filter(user = user).count(),
        }
    return render(request, 'account/profile.html', context)

@login_required
@transaction.atomic
def edit_profile(request):
    context = {}
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance = request.user)
        account_form = EditAccountForm(request.POST, request.FILES, instance = request.user.account)
        print(account_form.has_changed())
        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            context['user_form']= EditUserForm(instance=request.user)
            context['account_form'] = EditAccountForm(instance=request.user.account)
            context['success'] = True
        else:
            context['user_form']= user_form
            context['account_form'] = account_form
            context['success'] = False
    else:
        context['user_form'] = EditUserForm(instance=request.user)
        context['account_form'] = EditAccountForm(instance=request.user.account)
        context['success'] = None
    return render(request, 'account/edit_profile_form.html', context)

@login_required
@transaction.atomic
def edit_settings(request):
    context = {}
    if request.method == 'POST':
        password_form = PasswordChangeForm(data = request.POST, user = request.user)
        context['password_form']= password_form
        if password_form.is_valid():
            password_form.save()
            context['password_success'] = True
        else:
            context['password_success'] = False
        return render(request, 'account/edit_settings_form.html', context)                
    else:
        context['password_form'] = PasswordChangeForm(user = request.user)
        context['password_success'] = None
        return render(request, 'account/edit_settings_form.html', context)    

@login_required
@transaction.atomic
def delete_account(request):
    """doesn't actually delete, but clears all fields and sets is_active to False"""
    if request.method == "POST":
        password_confirm = PasswordConfirmForm(request.POST)
        if password_confirm.is_valid():
            password = password_confirm.cleaned_data.get('password')
            if request.user.check_password(password):
                request.user.account.top_albums = None #prevents models.PROTECT to be triggered
                request.user.delete()
                return render(request, 'account/deleted.html')
            else:
                return render(request, 'account/delete.html', {'form' : password_confirm, 'delete_success' : False})
        else:
            return render(request, 'account/delete.html', {'form' : password_confirm, 'delete_success' : False})         
    else:
        return render(request, 'account/delete.html', {'form' : PasswordConfirmForm()})

@login_required
def notifications(request):
    page = request.GET.get('page')
    all_notifications = request.user.notifications.all()
    p = Paginator(all_notifications, 20)
    try:
        notifications = p.page(page)
    except PageNotAnInteger:
        notifications = p.page(1)
    except EmptyPage:
        notifications = p.page(paginate.num_pages)
    context = {
        'notifications' : notifications,
        }
    rendered = render_to_string('account/notifications.html', context, request=request)
    p.object_list.mark_all_as_read()
    return HttpResponse(rendered)
