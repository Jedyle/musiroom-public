from django.test import TestCase, Client
from .models import *
from .views import register
from .forms import EditAccountForm, RegistrationForm
from lists.models import ItemList
from datetime import datetime, date, timedelta
from django.urls import clear_url_caches, get_resolver, get_urlconf, resolve, reverse
from django.core import mail

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
        self.assertRedirects(request, '/profil/connecte/', status_code = 302, target_status_code = 302)

    def status_code_login(self):
        c = Client()
        url = 'profil/connexion/'
        request = c.get(url, secure=(scheme == 'https'))
        self.assertEquals(request.status_code, 200)

    #chaque account a un top albums impossible à supprimer

"""
Register :
- test formulaire register (confirm password)
"""

class RegistrationFormTest(TestCase):

        
    def check_form(self, data, val):
        form = RegistrationForm(data)
        self.assertEquals(form.is_valid(), val)

    def check_form_serie(self, data, array, field, val):
        for elt in array:
            data['username'] = elt
            self.check_form(data, val)

    def test_valid(self):
        data = {
            'username' : 'toto',
            'password' : 'passe123456',
            'confirm_password' : 'passe123456',
            'email' : 'toto@domain.com',
            }
        self.check_form(data, True)
    
    def test_username_too_short(self):
        data = {
            'username' : 'toto',
            'password' : 'passe123456',
            'confirm_password' : 'passe123456',
            'email' : 'toto@domain.com',
            }        
        usernames = ['1', 'a', 'b', 'aa', 'bu', '12', '3a', '00']
        self.check_form_serie(data, usernames, 'username', False)
        
    def test_username_too_long(self):
        data = {
            'username' : 'toto',
            'password' : 'passe123456',
            'confirm_password' : 'passe123456',
            'email' : 'toto@domain.com',
            }
        usernames = ['aerihrfzuehfzoefhzrepfhzpfhzpufzpfgepf', 'zirijepjefrr2r5efref5efefeffefefz']
        self.check_form_serie(data, usernames, 'username', False)

    def test_passwords_differents(self):
        data = {
            'username' : 'toto',
            'password' : 'passe123456',
            'confirm_password' : 'passe1234567',
            'email' : 'toto@domain.com',
            }
        self.check_form(data, False)

    def test_username_forbidden_char(self):
        data = {
            'username' : 'toto@',
            'password' : 'passe123456',
            'confirm_password' : 'passe123456',
            'email' : 'toto@domain.com',
            }
        usernames = ['toto@', 'aaaaa^', '$toto', 't+oto']
        self.check_form_serie(data, usernames, 'username', False)
        
    def test_wrong_email(self):
        data = {
            'username' : 'toto',
            'password' : 'passe123456',
            'confirm_password' : 'passe123456',
            'email' : 'toto@domain',
            }
        emails = ['toto@domain','toto', 'toto@', '@domain.com', 'toto@domain..fr', 'toto@@domain.fr','toto@toto@domain.fr']
        self.check_form_serie(data, emails, 'email', False)
        

"""
Send email :
- resend et send donnent le même token
- click sur le lien => utilisateur devient actif
- click sur le lien deux fois => ne change rien
"""

class ConfirmationEmailTest(TestCase):

    def test_same_token_register_and_resend(self):
        c = Client()
        url = reverse('register')
        response = c.post(url, {'username' : 'Toto', 'email' : 'test@example.com', 'password' : 'pass12345', 'confirm_password' : 'pass12345'})
        self.assertEquals(response.status_code, 200)
        confirm_mail = mail.outbox[0]
        resend_url = reverse('resend_email', args=['Toto'])
        response = c.get(resend_url)
        self.assertEquals(response.status_code, 200)
        resent_mail = mail.outbox[1]
        self.assertEquals(confirm_mail.body, resent_mail.body)    

"""
Delete user :
- verif que la view delete fonctionne et supprime bien l'utilisateur
- delete ne fonctionne que si utilisateur connecte
"""

class DeleteUserTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username = 'Toto', password = 'pass12345', email = 'toto@test.fr')

        itemlist = ItemList(user = user, title='Top albums de Toto')
        itemlist.save()
        account = Account(user = user, top_albums = itemlist)        
        account.save()

    def test_delete_user(self):
        c = Client()
        url = reverse('login')
        login = c.post(url, {'username' : 'Toto', 'password': 'pass12345'})
        delete_url = reverse('delete_account')
        response = c.post(delete_url, {'password': 'pass12345'})
        self.assertEquals(response.status_code, 200)
        res = True
        try :
            user = User.objects.get(username = 'Toto')
            res = False
        except User.DoesNotExist:
            res = True
        self.assertEquals(res, True)

    def test_delete_not_logged(self):
        c = Client()
        delete_url = reverse('delete_account')
        response = c.post(delete_url, {'password': 'pass12345'})
        self.assertEquals(response.status_code, 302)  
        

class SearchAccountTest(TestCase):

    def setUp(self):
        user = User.objects.create_user(username = 'Toto', password = 'pass12345', email = 'toto@test.fr')

        itemlist = ItemList(user = user, title='Top albums de Toto')
        itemlist.save()
        account = Account(user = user, top_albums = itemlist)        
        account.save()
        
    def test_search_redirects_to_account(self):
        c = Client()
        url = reverse('albums:search')
        response = c.get(url, {'type' : 'user', 'query' : 'toto'})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Toto')
    
