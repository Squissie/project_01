"""
Django settings for svm project.

Generated by 'django-admin startproject' using Django 4.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""
from pathlib import Path
import os
from django.contrib.messages import constants as messages
from django.contrib.auth import get_user_model


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-k=4tc+v6syc2py$n^nysyca%f&e=xpyqv84vgz@#f3vv#1&56t"

# SECURITY WARNING: don't run with debug turned on in production!
## DEBUG SETTINGS
## show debug messages instead of 404
DEBUG = True
## use local media folder instead of AWS
DEBUG_NOAWS = True
## do not load model to save startup time
DEBUG_NOMODEL = False

ALLOWED_HOSTS = ["covidvisionx.herokuapp.com","127.0.0.1"]


# Application definition

INSTALLED_APPS = [
    # 'django.contrib.admin',
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "svmApp",
    "login_system.apps.UsersConfig",
    "django_filters",
    "bootstrap4",
    # "bootstrap_datepicker_plus",
    "storages",
    "django_cleanup.apps.CleanupConfig",
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

ROOT_URLCONF = "COVIDVisionX.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "template")],
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

WSGI_APPLICATION = "COVIDVisionX.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

if DEBUG_NOAWS:
    STATIC_URL = "/static/"
    MEDIA_URL = "/media/"

else:

    AWS_ACCESS_KEY_ID = "AKIAX5JY6267HMBNVMA2"
    AWS_SECRET_ACCESS_KEY = "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"
    AWS_S3_CUSTOM_DOMAIN = "fyp-covid19chestxray.s3.ap-southeast-1.amazonaws.com"
    AWS_STORAGE_BUCKET_NAME = "fyp-covid19chestxray"

    STATIC_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, "static")
    MEDIA_URL = "https://%s/%s/" % (AWS_S3_CUSTOM_DOMAIN, "media")

    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = None

    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3StaticStorage"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Path where media is stored
MEDIA_ROOT = BASE_DIR / "media"

# messages
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

MESSAGE_TAGS = {
    messages.DEBUG: "alert-info",
    messages.INFO: "alert-info",
    messages.SUCCESS: "alert-success",
    messages.WARNING: "alert-warning",
    messages.ERROR: "alert-danger",
}

AUTH_USER_MODEL = "login_system.User"

# Email Server
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_HOST_USER = "covidvisionx@gmail.com"
EMAIL_HOST_PASSWORD = "tclanbprmtttepkr"
EMAIL_USE_TLS = True

LOGIN_URL = "login"
