from django.test import TestCase, Client
from .models import *
from .views import register
from .forms import EditAccountForm, RegistrationForm
from lists.models import ItemList
from datetime import datetime, date, timedelta
from django.urls import clear_url_caches, get_resolver, get_urlconf, resolve, reverse

# Create your tests here.

class EditAccountFormTests(TestCase):

    def test_birth_in_future(self):
        data = {
            'display_name': True,
            'birth': date.today() + timedelta(days=5),
            'display_birth' : True,
            'sex' : 'M',
            'display_sex' : True,
            'description' : '',
            'avatar' : None
            }
        form = EditAccountForm(data = data)
        self.assertFalse(form.is_valid())

    def test_sex_not_in_choices(self):
        data = {
            'display_name': True,
            'birth': date.today() - timedelta(days=5),
            'display_birth' : True,
            'sex' : 'P',
            'display_sex' : True,
            'description' : '',
            'avatar' : None
            }
        form = EditAccountForm(data = data)
        self.assertFalse(form.is_valid())
        data['sex']='M'
        form = EditAccountForm(data = data)
        self.assertTrue(form.is_valid())
        data['sex']='F'
        form = EditAccountForm(data = data)
        self.assertTrue(form.is_valid())
        data['sex']='N'
        form = EditAccountForm(data = data)
        self.assertTrue(form.is_valid())

    def test_all(self):
        data = {
            'display_name': True,
            'birth': date.today() - timedelta(days=500),
            'display_birth' : True,
            'sex' : 'M',
            'display_sex' : True,
            'description' : '',
            'avatar' : None
            }
        form = EditAccountForm(data = data)
        self.assertTrue(form.is_valid())


class LoginRequiredTest(TestCase):

    #chaque user créé a un account, et les deux sont liés

    def setUp(self):
        user = User.objects.create_user(username = 'Toto', password = 'pass12345', email = 'toto@test.fr')

        itemlist = ItemList(user = user, title='Top albums de Toto')
        itemlist.save()
        account = Account(user = user, top_albums = itemlist)        
        account.save()

    def test_registration_creates_account(self):
        reg_form = {
            'username' : 'Risitas',
            'password' : 'password123',
            'confirm_password' : 'password123',
            'email' : 'test@test.org'
            }
        c = Client()
        c.post('/profil/inscription/', reg_form)
        user = User.objects.get(username = reg_form['username'])
        account = Account.objects.get(user = user)
        self.assertEqual(account.user, user)

    #/profil/modifier renvoie redirect si user pas co

    def test_account_page_not_logged(self):
        c = Client()
        url = reverse('edit_profile')
        request = c.get(url)
        self.assertRedirects(request, reverse('login')+'?next='+url)

    #/profil/parametres idem

    def test_settings_page_not_logged(self):
        c = Client()
        url = reverse('edit_settings')
        request = c.get(url)
        self.assertRedirects(request, reverse('login')+'?next='+url)

    #/profil/connecte idem

    def test_logged_page_not_logged(self):
        c = Client()
        url = reverse('loggedin')
        request = c.get(url)
        self.assertRedirects(request, reverse('login')+'?next='+url)


    #/profil/deconnexion idem

    def test_settings_page_not_logged(self):
        c = Client()
        url = reverse('logout')
        request = c.get(url)
        self.assertRedirects(request, '/')


    #/profil/connexion renvoie connecté si user déjà connecté

    def test_home_page_when_logged(self):
        c = Client()
        url = reverse('login')
        c.post(url, {'username' : 'Toto', 'password': 'pass12345'})
        request = c.get(url)
        print(request)
        self.assertRedirects(request, '/')

    def status_code_login(self):
        c = Client()
        url = 'profil/connexion/'
        request = c.get(url, secure=(scheme == 'https'))
        self.assertEquals(request.status_code, 200)
