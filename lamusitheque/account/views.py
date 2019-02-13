from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from friendship.models import Follow
from lists.models import ItemList, ListObject
from ratings.models import Review
from star_ratings.models import UserRating
from .forms import RegistrationForm, EditUserForm, EditAccountForm, PasswordConfirmForm
from .models import Account
from .tokens import account_activation_token


def send_activation_email(request, user):
    """
    Send an activation email to the newly registrated user
    :param request: the request object
    :param user: a (not active) user
    :return: nothing, sends an activation email to the user
    """
    current_site = get_current_site(request)
    mail_subject = 'Activez votre compte.'
    message = render_to_string('account/acc_active_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
        'token': account_activation_token.make_token(user),
    })
    to_email = user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()


def resend_email(request, username):
    """
    Resend an activation email if the first one has not been received
    :param request: request object
    :param username: the user's username
    :return: renders a template depending on the user's status (active or inactive)
    """
    user = User.objects.get(username=username)
    if request.user.is_authenticated and request.user != user:
        return redirect('/')
    if user.is_active:
        return render(request, 'account/already_confirmed.html', {})
    send_activation_email(request, user)
    return render(request, 'account/confirm_email.html', {'email': user.email, 'user': user})


@transaction.atomic
def register(request):
    """
    Registers a user (saves it in db, create its associated profile, top albums and sends a confirmation email
    :param request: request
    :return: renders a template
    """
    if request.user.is_authenticated:
        return redirect('/')
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            addr = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = User.objects.create_user(username=username, password=password, email=addr, is_active=False)
            profile = Account(user=user)
            top_albums = ItemList(user=user, title="Top Albums de " + user.username, ordered=True)
            top_albums.save()
            profile.top_albums = top_albums
            profile.save()
            send_activation_email(request, user)
            return render(request, 'account/confirm_email.html', {'email': addr, 'user': user})
        else:
            return render(request, 'account/registration_form.html', {'form': form, 'error': True})
    else:
        return render(request, 'account/registration_form.html', {'form': RegistrationForm()})


def activate(request, uidb64, token):
    """
    Sets the user status as active after he clicked on a confirmation link, and if the token is correct
    :param request:
    :param uidb64:
    :param token:
    :return:
    """
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        return redirect('registration_complete')
    else:
        if not user.is_active:
            return HttpResponse('Lien d\'activation invalide ou expiré.')
        else:
            return redirect('registration_complete')


def registration_complete(request):
    return render(request, 'account/registration_complete.html')


@login_required
def loggedin(request):
    return redirect('/')


def profile(request, username):
    """

    :param request:
    :param username:
    :return:
    """
    user = get_object_or_404(User, username=username)
    profile = user.account
    if request.user.is_authenticated:
        is_followed = Follow.objects.follows(user, request.user)
        follows = Follow.objects.follows(request.user, user)
    else:
        is_followed = None
        follows = None

    top_10 = ListObject.objects.filter(item_list=profile.top_albums).select_related('album')[:10]
    context = {
        'profile': profile,
        'top_10': top_10,
        'is_followed': is_followed,
        'follows': follows,
        'nb_reviews': Review.objects.filter(rating__user=user).count(),
        'nb_ratings': UserRating.objects.filter(user=user).count(),
    }
    return render(request, 'account/profile.html', context)


@login_required
@transaction.atomic
def edit_profile(request):
    context = {}
    if request.method == 'POST':
        user_form = EditUserForm(request.POST, instance=request.user)
        account_form = EditAccountForm(request.POST, request.FILES, instance=request.user.account)
        if user_form.is_valid() and account_form.is_valid():
            user_form.save()
            account_form.save()
            context['user_form'] = EditUserForm(instance=request.user)
            context['account_form'] = EditAccountForm(instance=request.user.account)
            context['success'] = True
        else:
            context['user_form'] = user_form
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
        password_form = PasswordChangeForm(data=request.POST, user=request.user)
        context['password_form'] = password_form
        if password_form.is_valid():
            password_form.save()
            context['password_success'] = True
        else:
            context['password_success'] = False
        return render(request, 'account/edit_settings_form.html', context)
    else:
        context['password_form'] = PasswordChangeForm(user=request.user)
        context['password_success'] = None
        return render(request, 'account/edit_settings_form.html', context)


@login_required
def user_exports(request):
    exports = request.user.exports.all().order_by('-created_at')
    return render(request, 'account/user_exports.html', {'exports': exports})


@login_required
@transaction.atomic
def delete_account(request):
    if request.method == "POST":
        password_confirm = PasswordConfirmForm(request.POST)
        if password_confirm.is_valid():
            password = password_confirm.cleaned_data.get('password')
            if request.user.check_password(password):
                request.user.account.top_albums = None  # prevents models.PROTECT to be triggered
                request.user.account.save()
                request.user.delete()
                return render(request, 'account/deleted.html')
            else:
                return render(request, 'account/delete.html', {'form': password_confirm, 'delete_success': False})
        else:
            return render(request, 'account/delete.html', {'form': password_confirm, 'delete_success': False})
    else:
        return render(request, 'account/delete.html', {'form': PasswordConfirmForm()})


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
        'notifications': notifications,
    }
    rendered = render_to_string('account/notifications.html', context, request=request)
    p.object_list.mark_all_as_read()
    return HttpResponse(rendered)


def search_account(request):
    m_type = request.GET.get('type')
    query = request.GET.get('query')
    page = request.GET.get('page')
    if not query or (m_type != 'user'):
        return redirect('/')
    else:
        if not page:
            page = 1
        list_account = User.objects.filter(username__icontains=query, is_active=True).order_by('username')
        paginate = Paginator(list_account, 12)
        try:
            accounts = paginate.page(page)
        except EmptyPage:
            accounts = paginate.page(paginate.num_pages)
        except PageNotAnInteger:
            accounts = paginate.page(1)
        accounts_and_followees = []
        for account in accounts:
            if request.user.is_anonymous:
                accounts_and_followees.append([account, None])
            else:
                accounts_and_followees.append([account, Follow.objects.follows(request.user, account)])

        context = {
            'accounts': accounts,
            'follows': accounts_and_followees,
            'paginate': (paginate.num_pages > 1),
            'query': query,
            'm_type': m_type,
            'page': page,
        }
        return render(request, 'account/search_account.html', context)
