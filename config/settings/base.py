"""
Django settings for icms project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os

import environ
import structlog
from django.forms import Field

BASE_DIR = environ.Path(__file__) - 3  # 2 level up ../..
env = environ.Env()

VCAP_SERVICES = env.json("VCAP_SERVICES", {})

LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/home"
LOGOUT_REDIRECT_URL = "/"

# Application definition
INSTALLED_APPS = [
    "web",
    "captcha",
    "compressor",
    "phonenumber_field",
    "guardian",
    "django_filters",
    "django_select2",
    "django.forms",
    "django_celery_results",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
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
    "django_structlog.middlewares.RequestMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [os.path.join(BASE_DIR, "web/templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "environment": "web.jinja2.environment",
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
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
            ],
        },
    },
]
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "web.auth.fox_hasher.FOXPBKDF2SHA1Hasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/2.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},  # NOQA
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Auth user model
AUTH_USER_MODEL = "web.user"

AUTHENTICATION_BACKENDS = [
    "web.auth.models.CustomBackend",
    "guardian.backends.ObjectPermissionBackend",
]

# Date formats
DATE_INPUT_FORMATS = ["%d-%b-%Y"]  # input formats
DATETIME_INPUT_FORMATS = ["%d-%b-%Y %H:%M:%S"]
DATE_FORMAT = ["d-M-Y"]  # format for displaying date
DATETIME_FORMAT = ["d-M-Y H:i:s"]

# Phone number format
PHONENUMBER_DB_FORMAT = "INTERNATIONAL"
PHONENUMBER_DEFAULT_REGION = "GB"

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
# USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static/")
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # other finders..
    "compressor.finders.CompressorFinder",
)

# Email
EMAIL_BACKEND = "django_ses.SESBackend"
AWS_SES_REGION_NAME = "eu-west-1"
AWS_SES_REGION_ENDPOINT = "email.eu-west-1.amazonaws.com"

# Modify required error messages globally
Field.default_error_messages = {
    "required": "You must enter this item",
}

# Upload to S3
# TODO: prefix this settings with CHUNK_UPLOADER_ when upstream library is pushed to registry
AWS_ACCESS_KEY_ID = "dev"
AWS_SECRET_ACCESS_KEY = "bar"
S3_APPEND_DATETIME_ON_UPLOAD = True
# AWS_REGION = 'us-west-2'
AWS_STORAGE_BUCKET_NAME = "icms.local"
AWS_S3_ENDPOINT_URL = "http://localstack:4572/"
S3_GENERATE_OBJECT_KEY_FUNCTION = "web.utils.s3upload.random_file_name"
S3_DOCUMENT_ROOT_DIRECTORY = "documents"
# END TODO

FILE_UPLOAD_HANDLERS = ("s3chunkuploader.file_handler.S3FileUploadHandler",)

# Anti virus settings
CLAM_AV_USERNAME = env.str("CLAM_AV_USERNAME", "test")
CLAM_AV_PASSWORD = env.str("CLAM_AV_PASSWORD", "")
CLAM_AV_URL = env.str("CLAM_AV_URL", "https://clamav.london.cloudapps.digital/v2/scan")

# Storage Folders
PATH_STORAGE_FIR = "/documents/fir/"  # start with /

# Structured logging shared configuration
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=structlog.threadlocal.wrap_dict(dict),
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Celery & Redis shared configuration
if "redis" in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]
else:
    REDIS_URL = env.str("REDIS_URL", "redis://redis:6379")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"

# Django cache with Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Default domain is used in email templates to pint users to ICMS from emails
DEFAULT_DOMAIN = env.str("ICMS_DEFAULT_DOMAIN", "http://localhost:8080/")

SELECT2_CACHE_BACKEND = "default"
SELECT2_CSS = os.path.join(STATIC_URL, "3rdparty/select2/select2.min.css")
SELECT2_JS = os.path.join(STATIC_URL, "3rdparty/select2/select2.min.js")

COMPANIES_HOUSE_TOKEN = os.environ.get("COMPANIES_HOUSE_TOKEN", "changeme")

# guardian config

GUARDIAN_MONKEY_PATCH = False
GUARDIAN_RENDER_403 = True
