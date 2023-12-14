"""
Django settings for decide project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
from dotenv import load_dotenv
import dj_database_url

load_dotenv()

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = "RENDER" not in os.environ

SECRET_KEY = "^##ydkswfu0+=ofw0l#$kv^8n)0$i(qd&d&ol#p9!b$8*5%j1+"

ALLOWED_HOSTS = []


# Application definition

SITE_ID = int(os.getenv("DJANGO_SITE_ID", "2"))
SOCIAL_AUTH_GITHUB_KEY = os.getenv("GITHUB_KEY", "")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("GITHUB_SECRET", "")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "django_filters",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_swagger",
    "gateway",
    "django.contrib.sites",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "social_django",
    "django_rest_passwordreset",
]

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "online",
        },
    }
}

SOCIAL_AUTH_GITHUB_SCOPE = ["user:email"]


LOGIN_REDIRECT_URL = "/"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ),
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.QueryParameterVersioning",
}

AUTHENTICATION_BACKENDS = [
    "base.backends.AuthBackend",
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
    "social_core.backends.github.GithubOAuth2",
]

MODULES = [
    "authentication",
    "base",
    "booth",
    "census",
    "mixnet",
    "postproc",
    "store",
    "visualizer",
    "voting",
]

BASEURL = "http://localhost:8000"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

ROOT_URLCONF = "decide.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "social_django.context_processors.backends",
            ],
        },
    },
]

WSGI_APPLICATION = "decide.wsgi.application"


# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "decide",
        "USER": "decide",
        "PASSWORD": "decide",
        "HOST": "localhost",
        "PORT": "5432",
    }
}


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


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = "es-es"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]


# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256

# Versioning
ALLOWED_VERSIONS = ["v1", "v2"]
DEFAULT_VERSION = "v1"


# Restore password
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR + "/sent_emails"

try:
    from local_settings import *
except ImportError:
    print("local_settings.py not found")

# loading jsonnet config
if os.path.exists("config.jsonnet"):
    import json
    from _jsonnet import evaluate_file

    config = json.loads(evaluate_file("config.jsonnet"))
    for k, v in config.items():
        vars()[k] = v


INSTALLED_APPS = INSTALLED_APPS + MODULES
