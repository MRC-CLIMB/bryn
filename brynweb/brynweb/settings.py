"""
Django settings for brynweb project.
"""

import os
import sentry_sdk

from django.contrib.messages import constants as messages
from sentry_sdk.integrations.django import DjangoIntegration

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

ALLOWED_HOSTS = []

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Application definition

INSTALLED_APPS = [
    "brynweb.apps.BrynAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "coverage",
    "huey.contrib.djhuey",
    "rest_framework",
    "widget_tweaks",
    "tinymce",
    "inline_actions",
    "core",
    "userdb",
    "home",
    "openstack",
    "discourse",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "brynweb.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "frontend/build/templates"),
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

WSGI_APPLICATION = "brynweb.wsgi.application"

# Custom message tags
MESSAGE_TAGS = {
    messages.ERROR: "is-danger",
    messages.INFO: "is-info",
    messages.SUCCESS: "is-success",
    messages.WARNING: "is-warning",
}


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Login settings

LOGIN_URL = "user:login"
LOGIN_REDIRECT_URL = "home:home"

# Don't reject auth where User.is_active is False; allows for custom error on email not-validated
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.AllowAllUsersModelBackend",
    "userdb.backends.UniqueEmailBackend",
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STATIC_ROOT = os.path.join(BASE_DIR, "../static")
STATIC_URL = "/static/"

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
    os.path.join(BASE_DIR, "frontend/build/static"),
]


# django-phonenumber-field settings

PHONENUMBER_DEFAULT_REGION = "GB"

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_THROTTLE_CLASSES": (
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ),
    "DEFAULT_THROTTLE_RATES": {"anon": "100/day", "user": "5000/day"},
    "DEFAULT_RENDERER_CLASSES": (
        "djangorestframework_camel_case.render.CamelCaseJSONRenderer",
        "djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer",
    ),
    "DEFAULT_PARSER_CLASSES": (
        "djangorestframework_camel_case.parser.CamelCaseFormParser",
        "djangorestframework_camel_case.parser.CamelCaseMultiPartParser",
        "djangorestframework_camel_case.parser.CamelCaseJSONParser",
    ),
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "handlers": {
        "console": {"level": "DEBUG", "class": "logging.StreamHandler"},
        "logfile": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR + "/../logfile",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "logfile"]},
}

# Lease & Licencing

SERVER_LEASE_DEFAULT_DAYS = 14
SERVER_LEASE_REMINDER_DAYS = [0, 1, 3, 5]
LICENCE_TERMINATION_DAYS = 90
LICENCE_RENEWAL_REMINDER_DAYS = [3, 7, 14, 28]

# Local secrets
try:
    from .locals import *  # noqa: F401,F403
except ImportError:
    pass

# Hashids

HASHIDS = {"SALT": HASHIDS_SALT, "MIN_LENGTH": 11}  # noqa: F405

# HUEY Task Scheduler

HUEY = {
    "huey_class": "huey.RedisHuey",
    "name": "bryn-huey",
    "immediate": DEBUG,
    "consumer": {"workers": 2},
}

# TinyMCE

TINYMCE_DEFAULT_CONFIG = {
    "theme": "silver",
    "height": 500,
    "menubar": False,
    "plugins": (
        "advlist,autolink,lists,link,image,charmap,print,preview,anchor,searchreplace,visualblocks,code,fullscreen,"
        "insertdatetime,media,table,paste,codesample,help,wordcount"
    ),
    "toolbar": (
        "undo redo | formatselect | bold italic backcolor | alignleft aligncenter alignright alignjustify | "
        "bullist numlist outdent indent | removeformat | codesample | code | help"
    ),
}

# SITE

#  For use in scheduled email tasks etc, where request is not available
# Helper template tag in core app '
SITE_SCHEME = "http"
SITE_DOMAIN = "localhost:8080"

# Sentry

sentry_sdk.init(
    dsn="https://02ed2c71582747179e83a1ccd77b7cda@o563550.ingest.sentry.io/5703634",
    integrations=[DjangoIntegration()],
    traces_sample_rate=0.3,
    send_default_pii=True,
)

if DEBUG:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
