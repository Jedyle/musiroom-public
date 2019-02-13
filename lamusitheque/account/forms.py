from datetime import date

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import get_default_password_validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinLengthValidator, MaxLengthValidator

from .models import Account, get_100_last_years


def ForbiddenUsernamesValidator(value):
    forbidden_usernames = ['admin', 'settings', 'news', 'about', 'help',
                           'signin', 'signup', 'signout', 'terms', 'privacy',
                           'cookie', 'new', 'login', 'logout', 'administrator',
                           'join', 'account', 'username', 'root', 'blog',
                           'user', 'users', 'billing', 'subscribe', 'reviews',
                           'review', 'blog', 'blogs', 'edit', 'mail', 'email',
                           'home', 'job', 'jobs', 'contribute', 'newsletter',
                           'shop', 'profile', 'register', 'auth',
                           'authentication', 'campaign', 'config', 'delete',
                           'remove', 'forum', 'forums', 'download',
                           'downloads', 'contact', 'blogs', 'feed', 'feeds',
                           'faq', 'intranet', 'log', 'registration', 'search',
                           'explore', 'rss', 'support', 'status', 'static',
                           'media', 'setting', 'css', 'js', 'follow',
                           'activity', 'questions', 'articles', 'network',
                           'inscription', 'connexion', 'deconnexion', 'connecte',
                           'profil', 'utilisateur', 'contact', 'parametre', 'parametres', 'passe_oublie',
                           'passe_oublie_fin', 'activation', 'modifier', 'oublie', 'musique', 'message', 'messages',
                           'notes', 'notifications', 'feedback', 'supprimer'
                           ]

    if value.lower() in forbidden_usernames:
        raise ValidationError('Ce nom est réservé.')


def InvalidUsernameValidator(value):
    if '@' in value or '+' in value:
        raise ValidationError('Entrez un pseudo valide.')


def UniqueEmailValidator(value):
    if User.objects.filter(email__iexact=value).exists():
        raise ValidationError('Un utilisateur avec cette adresse existe déjà.')


def UniqueUsernameIgnoreCaseValidator(value):
    if User.objects.filter(username__iexact=value).exists():
        raise ValidationError('Un utilisateur avec ce pseudo existe déjà.')


OnlyAlphanumericValidator = RegexValidator(
    regex='^[a-zA-Z0-9_-]*$',
    message='Un pseudo ne doit comporter que des lettres, chiffres et caractères _ et -',
    code='invalid_text'
)


def DateIsPastValidator(value):
    if value > date.today():
        raise ValidationError("La date choisie n'est pas encore passée.")


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        max_length=30,
        required=True,
        label="Pseudo",
        help_text='Un pseudo peut contenir des <strong>chiffres</strong>, des <strong>lettres</strong>, <strong>_</strong> et <strong>-</strong>')  # noqa: E501
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmez votre mot de passe",
        required=True)
    email = forms.CharField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        label="Adresse e-mail",
        required=True,
        max_length=75)

    class Meta:
        model = User
        exclude = ['last_login', 'date_joined']
        fields = ['username', 'email', 'password', 'confirm_password']

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['username'].validators.append(ForbiddenUsernamesValidator)
        self.fields['username'].validators.append(OnlyAlphanumericValidator)
        self.fields['username'].validators.append(UniqueUsernameIgnoreCaseValidator)
        self.fields['username'].validators.append(MinLengthValidator(3))
        self.fields['username'].validators.append(MaxLengthValidator(30))
        self.fields['password'].validators.extend(
            [validator.validate for validator in get_default_password_validators()])
        self.fields['email'].validators.append(UniqueEmailValidator)

    def clean(self):
        super(RegistrationForm, self).clean()
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and password != confirm_password:
            self._errors['password'] = self.error_class(
                ['Mots de passe différents'])
        return self.cleaned_data


class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = {'first_name', 'last_name'}


class EditAccountForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("display_name", "birth", "display_birth", "sex", "display_sex", "description", "avatar")
        labels = {
            'display_name': 'Afficher mon nom sur mon profil',
            'birth': 'Date de naissance',
            'display_birth': 'Afficher mon age sur mon profil',
            'sex': 'Sexe',
            'display_sex': 'Afficher sur mon profil',
            'description': "Description",
            'avatar': 'Avatar',
        }
        widgets = {
            'birth': forms.SelectDateWidget(empty_label=("Année", "Mois", "Jour"), years=get_100_last_years()),
            'avatar': forms.ClearableFileInput()
        }

    def __init__(self, *args, **kwargs):
        super(EditAccountForm, self).__init__(*args, **kwargs)
        self.fields['birth'].validators.append(DateIsPastValidator)
        self.field_order = ["display_name", "birth", "display_birth", "sex", "display_sex", "description", "avatar"]


class PasswordConfirmForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Mot de passe")

    class Meta:
        model = User
        fields = {'password'}
