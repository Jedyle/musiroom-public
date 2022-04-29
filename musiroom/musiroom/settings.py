"""
Django settings for musiroom project.

Generated by 'django-admin startproject' using Django 2.0.4.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import environ

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from pathlib import Path

from celery.schedules import crontab

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    MEDIA_ROOT=(str, BASE_DIR / "media"),
    STATIC_ROOT=(str, BASE_DIR / "media"),
    SENTRY_DSN=(str, ""),
)
environ.Env.read_env()

sentry_sdk.init(
    dsn=env("SENTRY_DSN"),
    integrations=[DjangoIntegration()],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=1.0,
    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = env("DEBUG")

BACKEND_URL = env("BACKEND_URL")
FRONTEND_URL = env("FRONTEND_URL")

# Application definition

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django_extensions",
    "debug_toolbar",
    "compressor",
    "django_unused_media",
    "django_forms_bootstrap",
    "rest_framework",
    "rest_framework_swagger",
    "django_filters",
    "rest_framework_filters",
    "rest_framework.authtoken",
    "rest_auth",
    "corsheaders",
    "generic_relations",
    "siteflags",
    "moderation",
    "user_profile",
    "albums",
    "lists",
    "conversations",
    "comments",
    "vote",
    "star_ratings",
    "reviews",
    "friendship",
    "ajax_follower",
    "jchart",
    "notifications",
    "feedback",
    "discussions",
    "search",
    "pinax.badges",
    "actstream",
    "django_social_share",
    "export_ratings",
]

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

SITE_ID = 4

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # "django.middleware.locale.LocaleMiddleware",
    "user_profile.middleware.UpdateLastActivityMiddleware",
]

INTERNAL_IPS = ["127.0.0.1"]
ALLOWED_HOSTS = ["*"]

ROOT_URLCONF = "musiroom.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "musiroom.wsgi.application"

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {"default": env.db()}  # reads env DATABASE_URL

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Caches

TEMPLATE_LOADERS = (
    (
        "django.template.loaders.cached.Loader",
        (
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ),
    ),
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
        "LOCATION": "/var/tmp/django_cache",
        "TIMEOUT": 3,
        "OPTIONS": {"MAX_ENTRIES": 1000},
    }
}

CACHE_TOP_ALBUMS_TIMEOUT = 1800

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "en"

TIME_ZONE = "Europe/Paris"

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (BASE_DIR / "locale/",)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"

# Add these new lines
STATICFILES_DIRS = (BASE_DIR / "static",)

STATIC_ROOT = BASE_DIR / "staticfiles"

LOGIN_URL = "/profil/connexion/"
LOGIN_REDIRECT_URL = "/profil/connecte/"
LOGOUT_REDIRECT_URL = "/"

# Mail server

EMAIL_USE_TLS = True
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
EMAIL_PORT = env("EMAIL_PORT")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")


# Media

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Star rating

STAR_RATINGS_RANGE = 10

#

CSRF_COOKIE_NAME = "XSRF-TOKEN"

# Comments

COMMENTS_MAX_DEPTH = 2
COMMENTS_ALLOWED_COMMENT_TARGETS = [
    "lists.models.ListObj",
    "discussions.models.Discussion",
    "reviews.models.Review",
]

# Notifications

DJANGO_NOTIFICATIONS_CONFIG = {
    "USE_JSONFIELD": True,
}

# Feedback

FEEDBACK_CHOICES = (
    ("bug", "Reporter un bug"),
    ("suggestion", "Faire une suggestion"),
    ("signal", "Signaler un comportement"),
    ("album", "Rapporter un album non présent sur le site"),
)
ALLOW_ANONYMOUS_FEEDBACK = True

# Albums

YOUTUBE_API_KEY = env("YOUTUBE_API_KEY")


# Discussion settings

# default : title
DISCUSSIONS_SEARCH_FIELDS = {
    "album": "title",
    "artist": "name",
}

# Autocomplete settings

AUTOCOMPLETE_SEARCH_FIELDS = {
    "album": "title",
    "artist": "name",
    "user": "username",
}

# User absolute url

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/api/users/%s/" % o.username,
}

# CELERY / RABBITMQ

CELERY_BROKER_URL = env("CELERY_BROKER_URL")

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONEC = "Europe/Paris"

CELERY_BEAT_SCHEDULE = {
    "update-badges": {
        "task": "user_profile.tasks.update_badges",
        "schedule": crontab(minute=1, hour=2),
    },
}

# Activity

ACTSTREAM_SETTINGS = {"USE_JSONFIELD": True}

ACTIVITY_ITEMS_PER_PAGE = 10

# Exports

MIN_EXPORT_TIMEDIFF = 0

# REST FRAMEWORK

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "musiroom.apiutils.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": (
        "rest_framework_filters.backends.RestFrameworkFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
}

# ALLAUTH

profile_EMAIL_VERIFICATION = "mandatory"
profile_EMAIL_REQUIRED = True

# REST AUTh

REST_AUTH_SERIALIZERS = {
    "USER_DETAILS_SERIALIZER": "user_profile.api.serializers.UserProfileSerializer",
}

OLD_PASSWORD_FIELD_ENABLED = True

# CORS

CORS_ORIGIN_ALLOW_ALL = True

# FRONTEND

FRONTEND_APP_NAME = env("FRONTEND_APP_NAME")
