
"""
Django settings for review_project project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from celery.schedules import crontab

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '0s9p5k^@^uhv@58@-6$4ri84bzw26pbyp*y-^fupj)5sl=up-n'

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'debug_toolbar',
    'django_unused_media',
    'django_forms_bootstrap',
    'rest_framework',
    'siteflags',
    'moderation',
    'core',
    'account',
    'albums',
    'lists',
    'postman',
    'vote',
    'star_ratings',
    'ratings',
    'django_comments_xtd',
    'django_comments',
    'friendship',
    'ajax_follower',
    'jchart',
    'notifications',
    'feedback',
    'discussions',
    'autocomplete_search',
    'pinax.badges',
    ]

SITE_ID = 4

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
]

INTERNAL_IPS = ['127.0.0.1']

ROOT_URLCONF = 'review_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [(os.path.join(BASE_DIR, 'templates')),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'review_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'reviews_bis',
        'USER': 'jeremy',
        'PASSWORD': '',
        'HOST': '',
        'PORT' : '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


#Caches

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache',
        'TIMEOUT': 30,
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'fr'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

# Add these new lines
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

LOGIN_URL = '/profil/connexion/'
LOGIN_REDIRECT_URL = '/profil/connecte/'
LOGOUT_REDIRECT_URL = '/'


# Mail server

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'darknessjdl@gmail.com'
EMAIL_HOST_PASSWORD = 'dumbpassword3'
EMAIL_PORT = 587

#Media

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

#Messaging (postman) app

POSTMAN_I18N_URLS = True
POSTMAN_DISALLOW_ANONYMOUS = True
POSTMAN_DISABLE_USER_EMAILING = True
POSTMAN_AUTO_MODERATE_AS = True


# Star rating

STAR_RATINGS_RANGE = 10

#

CSRF_COOKIE_NAME = "XSRF-TOKEN"

# Comments

CRISPY_TEMPLATE_PACK = 'bootstrap3'

COMMENTS_APP = 'django_comments_xtd'

COMMENTS_XTD_MAX_THREAD_LEVEL = 1  # default is 0
COMMENTS_XTD_MAX_THREAD_LEVEL_BY_APP_MODEL = {
    'discussions.discussion' : 3,
    }

COMMENTS_XTD_LIST_ORDER = ('thread_id', 'order')

COMMENTS_XTD_APP_MODEL_OPTIONS = {
    'default': {
        'allow_flagging': True,
        'allow_feedback': True,
        'show_feedback': True,
    }
}

# Notifications

DJANGO_NOTIFICATIONS_CONFIG = {
    'USE_JSONFIELD' : True,
}

# Feedback

FEEDBACK_CHOICES = (
        ('bug', 'Reporter un bug'),
        ('suggestion', 'Faire une suggestion'),
    ('signal', 'Signaler un comportement'),
    ('album', 'Rapporter un album non présent sur le site')
)
ALLOW_ANONYMOUS_FEEDBACK = True


# Discussion settings

#default : title
DISCUSSIONS_SEARCH_FIELDS = {
    'album' : 'title',
    'artist' : 'name',
    }


# Autocomplete settings

AUTOCOMPLETE_SEARCH_FIELDS = {
    'album' : 'title',
    'artist' : 'name',
    'user' : 'username',
    }



# User absolute url

ABSOLUTE_URL_OVERRIDES = {
    'auth.user': lambda o: "/profil/u/%s" % o.username,
}


# CELERY / RABBITMQ

CELERY_BROKER_URL = "amqp://jeremy:dumbpassword3@localhost:5672/jeremy_vhost"

CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
	
CELERY_TIMEZONEC  = 'Europe/Paris'


CELERY_BEAT_SCHEDULE = {
    'update-badges': {
        'task': 'account.tasks.update_badges',
        'schedule': crontab(minute=1, hour=2),
    },
}
