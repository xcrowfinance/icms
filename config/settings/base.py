"""
Django settings for icms project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""
import os
import ssl

import environ
import structlog
from django.forms import Field

BASE_DIR = environ.Path(__file__) - 3  # 2 level up ../..
env = environ.Env()

VCAP_SERVICES = env.json("VCAP_SERVICES", default={})

# Application definition
DEBUG = env.bool("ICMS_DEBUG", False)
WSGI_APPLICATION = "config.wsgi.application"
APP_ENV = env.str("APP_ENV", default="notset")

INSTALLED_APPS = [
    "web",
    "data_migration",
    "compressor",
    "phonenumber_field",
    "guardian",
    "django_chunk_upload_handlers",
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
    "django.contrib.sites",
    # STAFF-SSO client app
    "authbroker_client",
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
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django_structlog.middlewares.RequestMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    "web.middleware.common.ICMSMiddleware",
    "web.middleware.one_login.UserFullyRegisteredMiddleware",
]

ROOT_URLCONF = "config.urls"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-FORM_RENDERER
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

TEMPLATES = [
    # Jinja defined for IMCS templates.
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
                "web.permissions.context_processors.request_user_object_permissions",
                "web.auth.context_processors.auth",
                "web.sites.context_processors.sites",
            ],
        },
    },
    # DjangoTemplates defined for Django admin application.
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

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "web.auth.fox_hasher.FOXPBKDF2SHA1Hasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",  # /PS-IGNORE
    "django.contrib.auth.hashers.Argon2PasswordHasher",
]

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Auth user model
AUTH_USER_MODEL = "web.user"

AUTHENTICATION_BACKENDS = ["web.auth.backends.ModelAndObjectPermissionBackend"]

#
# STAFF-SSO client app settings
AUTHBROKER_URL = env.str("STAFF_SSO_AUTHBROKER_URL", default="")
AUTHBROKER_CLIENT_ID = env.str("STAFF_SSO_AUTHBROKER_CLIENT_ID", default="")
AUTHBROKER_CLIENT_SECRET = env.str("STAFF_SSO_AUTHBROKER_CLIENT_SECRET", default="")
AUTHBROKER_STAFF_SSO_SCOPE = env.str("STAFF_SSO_AUTHBROKER_STAFF_SSO_SCOPE", default="")
AUTHBROKER_ANONYMOUS_PATHS = env.list("STAFF_SSO_AUTHBROKER_ANONYMOUS_PATHS", default=[])
AUTHBROKER_ANONYMOUS_URL_NAMES = env.list("STAFF_SSO_AUTHBROKER_ANONYMOUS_URL_NAMES", default=[])

#
# GOV.UK One Login settings
GOV_UK_ONE_LOGIN_CLIENT_ID = env.str("GOV_UK_ONE_LOGIN_CLIENT_ID", default="")
GOV_UK_ONE_LOGIN_CLIENT_SECRET = env.str("GOV_UK_ONE_LOGIN_CLIENT_SECRET", default="")
GOV_UK_ONE_LOGIN_SCOPE = env.str("GOV_UK_ONE_LOGIN_SCOPE", default="")
GOV_UK_ONE_LOGIN_OPENID_CONFIG_URL = env.str("GOV_UK_ONE_LOGIN_OPENID_CONFIG_URL", default="")

#
# Authentication feature flags
STAFF_SSO_ENABLED = env.bool("STAFF_SSO_ENABLED", True)
GOV_UK_ONE_LOGIN_ENABLED = env.bool("GOV_UK_ONE_LOGIN_ENABLED", True)

LOGIN_URL = "login-start"
LOGIN_REDIRECT_URL = "workbasket"
# Do not use this (all handled in "logout-user")
LOGOUT_REDIRECT_URL = None


if STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS.append("web.auth.backends.ICMSStaffSSOBackend")

if GOV_UK_ONE_LOGIN_ENABLED:
    AUTHENTICATION_BACKENDS.append("web.auth.backends.ICMSGovUKOneLoginBackend")

# Email
GOV_NOTIFY_API_KEY = env.str("GOV_NOTIFY_API_KEY", default="")
EMAIL_BACKEND = env.str("EMAIL_BACKEND", default="django.core.mail.backends.console.EmailBackend")

# Email/phone contacts
EMAIL_FROM = env.str("ICMS_EMAIL_FROM", default="")
ILB_CONTACT_EMAIL = env.str("ICMS_ILB_CONTACT_EMAIL", default="")
ILB_GSI_CONTACT_EMAIL = env.str("ICMS_ILB_GSI_CONTACT_EMAIL", default="")
ILB_CONTACT_PHONE = env.str("ICMS_ILB_CONTACT_PHONE", default="")
ILB_CONTACT_NAME = env.str("ICMS_ILB_CONTACT_NAME", default="")
ILB_CONTACT_ADDRESS = env.str("ICMS_ILB_CONTACT_ADDRESS", default="")
ICMS_FIREARMS_HOMEOFFICE_EMAIL = env.str("ICMS_FIREARMS_HOMEOFFICE_EMAIL", default="")
ICMS_CFS_HSE_EMAIL = env.str("ICMS_CFS_HSE_EMAIL", default="")
ICMS_GMP_BEIS_EMAIL = env.str("ICMS_GMP_BEIS_EMAIL", default="")

# File storage
# for https://github.com/uktrade/django-chunk-s3-av-upload-handlers
if "aws-s3-bucket" in VCAP_SERVICES:
    app_bucket_creds = VCAP_SERVICES["aws-s3-bucket"][0]["credentials"]
else:
    app_bucket_creds = {}

AWS_REGION = app_bucket_creds.get("aws_region")
AWS_ACCESS_KEY_ID = app_bucket_creds.get("aws_access_key_id")
AWS_SECRET_ACCESS_KEY = app_bucket_creds.get("aws_secret_access_key")
AWS_STORAGE_BUCKET_NAME = app_bucket_creds.get("bucket_name")

# Phone number format
PHONENUMBER_DB_FORMAT = "INTERNATIONAL"
PHONENUMBER_DEFAULT_REGION = "GB"

# Internationalization
# https://docs.djangoproject.com/en/2.1/topics/i18n/
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
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

# Modify required error messages globally
Field.default_error_messages = {
    "required": "You must enter this item",
}

# Root directory for s3 bucket
S3_ROOT_DIRECTORY = "documents"

# Used to set the S3 endpoint in development environments only
AWS_S3_ENDPOINT_URL: str | None = None

# Order is important
FILE_UPLOAD_HANDLERS = (
    "django_chunk_upload_handlers.clam_av.ClamAVFileUploadHandler",
    "django_chunk_upload_handlers.s3.S3FileUploadHandler",
)

# Anti virus settings
CLAM_AV_USERNAME = env.str("CLAM_AV_USERNAME", default="test")
CLAM_AV_PASSWORD = env.str("CLAM_AV_PASSWORD", default="")
CLAM_AV_DOMAIN = env.str("CLAM_AV_DOMAIN", default="clamav.london.cloudapps.digital")

# Storage Folders
PATH_STORAGE_FIR = "/documents/fir/"  # start with /

# Celery & Redis shared configuration
if "redis" in VCAP_SERVICES:
    REDIS_URL = VCAP_SERVICES["redis"][0]["credentials"]["uri"]
    CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_REQUIRED}

else:
    REDIS_URL = env.str("REDIS_URL", default="redis://redis:6379")

CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = "django-db"
CELERY_CACHE_BACKEND = REDIS_URL
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_RESULT_SERIALIZER = "json"
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_EXTENDED = True

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

# Age in seconds
SESSION_COOKIE_AGE = env.int("DJANGO_SESSION_COOKIE_AGE", default=60 * 30)

# Secure cookies only
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SELECT2_CACHE_BACKEND = "default"
SELECT2_CSS = os.path.join(STATIC_URL, "3rdparty/select2/select2.min.css")
SELECT2_JS = os.path.join(STATIC_URL, "3rdparty/select2/select2.min.js")

COMPANIES_HOUSE_DOMAIN = os.environ.get(
    "COMPANIES_HOUSE_DOMAIN", "https://api.companieshouse.gov.uk/"
)

# To view / change this token log in to the following: https://developer.company-information.service.gov.uk
# Login details can be found in passman, this requires icms group access.
# Once logged in, navigate to the following
# Manage Applications  -> View All Applications -> ICMS
COMPANIES_HOUSE_TOKEN = os.environ.get("COMPANIES_HOUSE_TOKEN", "changeme")

# guardian config
# https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html#custom-user-model
GUARDIAN_MONKEY_PATCH = False
GUARDIAN_RENDER_403 = True
# https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html#anonymous-user-creation
GUARDIAN_GET_INIT_ANONYMOUS_USER = "web.auth.backends.get_anonymous_user_instance"

# Used to add dummy test in non prod environments
ALLOW_DISASTROUS_DATA_DROPS_NEVER_ENABLE_IN_PROD = env.bool(
    "ALLOW_DISASTROUS_DATA_DROPS_NEVER_ENABLE_IN_PROD", default=False
)

# Used to bypass chief in non prod environments
ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD = env.bool(
    "ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD", default=False
)

# getAddress.io api key for post code search
ADDRESS_API_KEY = env.str("ICMS_ADDRESS_API_KEY", default="")

SILENCED_SYSTEM_CHECKS = env.list("ICMS_SILENCED_SYSTEM_CHECKS", default=[])
SILENCED_SYSTEM_CHECKS.extend(
    [
        # Guardian authentication backend is not hooked (Replaced with ModelAndObjectPermissionBackend).
        "guardian.W001",
    ]
)

# minifi html (django-htmlmin)
HTML_MINIFY = True

# Django Compressor
COMPRESS_OFFLINE = True

# ICMS-HMRC settings
SEND_LICENCE_TO_CHIEF = env.bool("SEND_LICENCE_TO_CHIEF", default=False)
ICMS_HMRC_DOMAIN = env.str(
    "ICMS_HMRC_DOMAIN", default="https://icms-hmrc.trade.dev.uktrade.digital/"
)
ICMS_HMRC_UPDATE_LICENCE_ENDPOINT = env.str(
    "ICMS_HMRC_UPDATE_LICENCE_ENDPOINT", default="mail/update-licence/"
)
HAWK_AUTH_ID = env.str("HAWK_AUTH_ID", default="icms")
HAWK_AUTH_KEY = env.str("HAWK_AUTH_KEY", default="secret")

# CHIEF spec: quantityIssued n(11).n(3) decimal field with up to n digits before the decimal point and
# up to m digits after.
# This validation would normally be done in the model e.g. models.DecimalField(max_digits=14, decimal_places=3)
# But PositiveBigIntegerField was required to migrate legacy records.
# So this constant is used in the Firearm Goods forms
CHIEF_MAX_QUANTITY = 99_999_999_999.999

# Data migration settings
ALLOW_DATA_MIGRATION = env.bool("ALLOW_DATA_MIGRATION", default=False)
ICMS_V1_REPLICA_USER = env.str("ICMS_V1_REPLICA_USER", default="")
ICMS_V1_REPLICA_PASSWORD = env.str("ICMS_V1_REPLICA_PASSWORD", default="")
ICMS_V1_REPLICA_DSN = env.str("ICMS_V1_REPLICA_DSN", default="")
ICMS_PROD_USER = env.str("ICMS_PROD_USER", default="")
ICMS_PROD_PASSWORD = env.str("ICMS_PROD_PASSWORD", default="")

# Workbasket pagination setting
WORKBASKET_PER_PAGE = env.int("WORKBASKET_PER_PAGE", 100)

# Set to true to mark inactive application types active when running add_dummy_data.py
SET_INACTIVE_APP_TYPES_ACTIVE = env.bool("SET_INACTIVE_APP_TYPES_ACTIVE", default=False)

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

# Print json formatted logs to console. We override this for local development
# and testing.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json_formatter": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json_formatter",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "ERROR",
        },
        "web": {
            "handlers": ["console"],
            "level": "INFO",
        },
        # https://github.com/Kozea/WeasyPrint/issues/412#issuecomment-1724928357
        "fontTools.subset": {"propagate": False},
    },
}
