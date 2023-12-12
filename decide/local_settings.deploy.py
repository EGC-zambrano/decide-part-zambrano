import os
import dj_database_url

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

SECRET_KEY = os.environ.get("SECRET_KEY")

DEBUG = "RENDER" not in os.environ

# Modules in use, commented modules that you won't use
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
    "allauth.account.middleware.AccountMiddleware",
]

STATIC_URL = "/static/"


# if not DEBUG:
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

BASEURL = "https://{}".format(os.environ.get("RENDER_EXTERNAL_HOSTNAME"))
SITE_ID = int(os.getenv("DJANGO_SITE_ID", "2"))
SOCIAL_AUTH_GITHUB_KEY = os.getenv("GITHUB_KEY", "")
SOCIAL_AUTH_GITHUB_SECRET = os.getenv("GITHUB_SECRET", "")

APIS = {
    "authentication": BASEURL,
    "base": BASEURL,
    "booth": BASEURL,
    "census": BASEURL,
    "mixnet": BASEURL,
    "postproc": BASEURL,
    "store": BASEURL,
    "visualizer": BASEURL,
    "voting": BASEURL,
}

DATABASE_URL = os.environ.get("DATABASE_URL")
DATABASES = {"default": dj_database_url.parse(DATABASE_URL)}

ALLOWED_ORIGINS = ["https://{}".format(os.environ.get("RENDER_EXTERNAL_HOSTNAME"))]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Strict"
CSRF_TRUSTED_ORIGINS = ALLOWED_ORIGINS.copy()

# number of bits for the key, all auths should use the same number of bits
KEYBITS = 256
