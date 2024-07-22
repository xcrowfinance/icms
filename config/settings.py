"""
Django settings for icms project.

Generated by 'django-admin startproject' using Django 2.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.1/ref/settings/
"""

import copy
import os
import ssl
from pathlib import Path
from typing import Any

import jinja2
from dbt_copilot_python.utility import is_copilot
from django.forms import Field
from django_log_formatter_asim import ASIMFormatter

from config.env import env
from web.one_login import types as one_login_types
from web.utils.sentry import init_sentry

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR: Path = Path(__file__).resolve().parent.parent

# Application definition
DEBUG = env.debug
WSGI_APPLICATION = "config.wsgi.application"
APP_ENV = env.app_env
SECRET_KEY = env.secret_key
ALLOWED_HOSTS = env.allowed_hosts_list
FIXTURE_DIRS = [
    BASE_DIR / "data_migration/management/commands/fixtures",
    BASE_DIR / "web/management/commands/fixtures",
]

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
    "web.middleware.common.ICMSCurrentSiteMiddleware",
    "htmlmin.middleware.HtmlMinifyMiddleware",
    "htmlmin.middleware.MarkRequestMiddleware",
    "web.middleware.common.ICMSMiddleware",
    "web.middleware.one_login.UserFullyRegisteredMiddleware",
    "csp.middleware.CSPMiddleware",
    "web.middleware.common.SetPermittedCrossDomainPolicyHeaderMiddleware",
]

ROOT_URLCONF = "config.urls"

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

DATABASES = env.database_config

# https://docs.djangoproject.com/en/4.2/ref/settings/#std-setting-FORM_RENDERER
FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

TEMPLATES = [
    # Jinja defined for IMCS templates.
    {
        "BACKEND": "django.template.backends.jinja2.Jinja2",
        "DIRS": [BASE_DIR / "web/templates"],
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

# Extended later if staff-sso or one-login are enabled.
AUTHENTICATION_BACKENDS = ["web.auth.backends.ModelAndObjectPermissionBackend"]

#
# STAFF-SSO client app settings
AUTHBROKER_URL = env.staff_sso_authbroker_url
AUTHBROKER_CLIENT_ID = env.staff_sso_authbroker_client_id
AUTHBROKER_CLIENT_SECRET = env.staff_sso_authbroker_client_secret
AUTHBROKER_STAFF_SSO_SCOPE = env.staff_sso_authbroker_staff_sso_scope
AUTHBROKER_ANONYMOUS_PATHS = env.staff_sso_authbroker_anonymous_paths
AUTHBROKER_ANONYMOUS_URL_NAMES = env.staff_sso_authbroker_anonymous_url_names

#
# GOV.UK One Login settings
GOV_UK_ONE_LOGIN_OPENID_CONFIG_URL = env.gov_uk_one_login_openid_config_url
GOV_UK_ONE_LOGIN_SCOPE = env.gov_uk_one_login_scope
GOV_UK_ONE_LOGIN_GET_CLIENT_CONFIG_PATH = env.gov_uk_one_login_get_client_config_path
GOV_UK_ONE_LOGIN_IMPORTER_CLIENT_ID = env.gov_uk_one_login_importer_client_id
GOV_UK_ONE_LOGIN_IMPORTER_CLIENT_SECRET = env.gov_uk_one_login_importer_client_secret
GOV_UK_ONE_LOGIN_EXPORTER_CLIENT_ID = env.gov_uk_one_login_exporter_client_id
GOV_UK_ONE_LOGIN_EXPORTER_CLIENT_SECRET = env.gov_uk_one_login_exporter_client_secret
GOV_UK_ONE_LOGIN_AUTHENTICATION_LEVEL = one_login_types.AuthenticationLevel.MEDIUM_LEVEL
GOV_UK_ONE_LOGIN_CONFIDENCE_LEVEL = one_login_types.IdentityConfidenceLevel.NONE

#
# Authentication feature flags
STAFF_SSO_ENABLED = env.staff_sso_enabled
GOV_UK_ONE_LOGIN_ENABLED = env.gov_uk_one_login_enabled

LOGIN_URL = "login-start"
LOGIN_REDIRECT_URL = "workbasket"
# Do not use this (all handled in "logout-user")
LOGOUT_REDIRECT_URL = None

if STAFF_SSO_ENABLED:
    AUTHENTICATION_BACKENDS.append("web.auth.backends.ICMSStaffSSOBackend")

if GOV_UK_ONE_LOGIN_ENABLED:
    AUTHENTICATION_BACKENDS.append("web.auth.backends.ICMSGovUKOneLoginBackend")

# Email
GOV_NOTIFY_API_KEY = env.gov_notify_api_key
EMAIL_BACKEND = env.email_backend

MAIL_TASK_RATE_LIMIT = env.mail_task_rate_limit
MAIL_TASK_RETRY_JITTER = env.mail_task_retry_jitter
MAIL_TASK_MAX_RETRIES = env.mail_task_max_retries

# Same logic here: icms/web/mail/decorators.py
if APP_ENV in ("local", "dev", "uat", "staging"):
    SEND_ALL_EMAILS_TO = env.send_all_emails_to
else:
    SEND_ALL_EMAILS_TO = []

# Email/phone contacts
EMAIL_FROM = env.email_from
ILB_CONTACT_EMAIL = env.ilb_contact_email
ILB_GSI_CONTACT_EMAIL = env.ilb_gsi_contact_email
ILB_CONTACT_PHONE = env.ilb_contact_phone
ILB_CONTACT_NAME = env.ilb_contact_name
ILB_CONTACT_ADDRESS = env.ilb_contact_address
ICMS_FIREARMS_HOMEOFFICE_EMAIL = env.firearms_homeoffice_email
ICMS_CFS_HSE_EMAIL = env.cfs_hse_email
ICMS_GMP_BEIS_EMAIL = env.gmp_beis_email

# File storage
# for https://github.com/uktrade/django-chunk-s3-av-upload-handlers

app_bucket_creds = env.s3_bucket_config
AWS_REGION = app_bucket_creds.get("aws_region")
AWS_STORAGE_BUCKET_NAME = app_bucket_creds.get("bucket_name")

if not is_copilot():
    # Only required in Cloud Foundry.
    AWS_ACCESS_KEY_ID = app_bucket_creds.get("aws_access_key_id")
    AWS_SECRET_ACCESS_KEY = app_bucket_creds.get("aws_secret_access_key")

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
STATIC_ROOT = BASE_DIR / "static/"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # other finders.
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
CLAM_AV_USERNAME = env.clam_av_username
CLAM_AV_PASSWORD = env.clam_av_password
CLAM_AV_DOMAIN = env.clam_av_domain

# Storage Folders
PATH_STORAGE_FIR = "/documents/fir/"  # start with /

# Celery & Redis shared configuration
REDIS_URL = env.redis_url
# Set use_SSL as we are deployed to CF or DBT Platform
if REDIS_URL not in [env.local_redis_url, ""]:
    CELERY_BROKER_USE_SSL = {"ssl_cert_reqs": ssl.CERT_REQUIRED}

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
    },
    "django_compressor_cache": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# Age in seconds
SESSION_COOKIE_AGE = env.django_session_cookie_age

# Secure cookies only
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SELECT2_CACHE_BACKEND = "default"
SELECT2_CSS = os.path.join(STATIC_URL, "3rdparty/select2/select2.min.css")
SELECT2_JS = os.path.join(STATIC_URL, "3rdparty/select2/select2.min.js")

COMPANIES_HOUSE_DOMAIN = env.companies_house_domain
# To view / change this token log in to the following: https://developer.company-information.service.gov.uk
# Login details can be found in passman, this requires icms group access.
# Once logged in, navigate to the following
# Manage Applications  -> View All Applications -> ICMS
COMPANIES_HOUSE_TOKEN = env.companies_house_token

# guardian config
# https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html#custom-user-model
GUARDIAN_MONKEY_PATCH = False
GUARDIAN_RENDER_403 = True
# https://django-guardian.readthedocs.io/en/stable/userguide/custom-user-model.html#anonymous-user-creation
GUARDIAN_GET_INIT_ANONYMOUS_USER = "web.auth.backends.get_anonymous_user_instance"

# Used to bypass chief in non prod environments
ALLOW_BYPASS_CHIEF_NEVER_ENABLE_IN_PROD = env.allow_bypass_chief_never_enable_in_prod

# getAddress.io api key for post code search
ADDRESS_API_KEY = env.address_api_key

SILENCED_SYSTEM_CHECKS = env.silenced_system_checks
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
# COMPRESS_CACHE_BACKEND default value is "default" which for ICMS is a redis cache
# There is no redis connection at build time in DBT Platform so have a specific cache for
# django-compressor to use.
COMPRESS_CACHE_BACKEND = "django_compressor_cache"

# ICMS-HMRC settings
SEND_LICENCE_TO_CHIEF = env.send_licence_to_chief
ICMS_HMRC_DOMAIN = env.icms_hmrc_domain
ICMS_HMRC_UPDATE_LICENCE_ENDPOINT = env.icms_hmrc_update_licence_endpoint
HAWK_AUTH_ID = env.hawk_auth_id
HAWK_AUTH_KEY = env.hawk_auth_key

# CHIEF spec: quantityIssued n(11).n(3) decimal field with up to n digits before the decimal point and
# up to m digits after.
# This validation would normally be done in the model e.g. models.DecimalField(max_digits=14, decimal_places=3)
# But PositiveBigIntegerField was required to migrate legacy records.
# So this constant is used in the Firearm Goods forms
CHIEF_MAX_QUANTITY = 99_999_999_999.999

# Data migration settings
ALLOW_DATA_MIGRATION = env.allow_data_migration
ICMS_V1_REPLICA_USER = env.v1_replica_user
ICMS_V1_REPLICA_PASSWORD = env.v1_replica_password
ICMS_V1_REPLICA_DSN = env.v1_replica_dsn
ICMS_PROD_USER = env.prod_user
ICMS_PROD_PASSWORD = env.prod_password
DATA_MIGRATION_EMAIL_DOMAIN_EXCLUDE = env.data_migration_email_domain_exclude

# Workbasket pagination setting
WORKBASKET_PER_PAGE = env.workbasket_per_page

# Set to true to mark inactive application types active when running add_dummy_data.py
SET_INACTIVE_APP_TYPES_ACTIVE = env.set_inactive_app_types_active

LOGGING: dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "asim_formatter": {
            "()": ASIMFormatter,
        },
        "simple": {
            "style": "{",
            "format": "{asctime} {levelname} {message}",
        },
    },
    "handlers": {
        "asim": {
            "class": "logging.StreamHandler",
            "formatter": "asim_formatter",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "mohawk": {"level": "INFO"},
    },
}

# Django Log Formatter ASIM settings
# is_copilot() evaluates to True locally now so also check env.app_env
# This was done to use DBTPlatformEnvironment instead of CloudFoundryEnvironment going forward.
if is_copilot() and env.app_env != "local":
    DLFA_TRACE_HEADERS = ("X-B3-TraceId", "X-B3-SpanId")

    # Set the correct handlers when running in DBT Platform
    # console handler set as default as it's easier to read
    LOGGING["root"]["handlers"] = ["asim"]
    LOGGING["loggers"]["django"]["handlers"] = ["asim"]

# Initialise Sentry if enabled
if env.sentry_enabled:
    init_sentry(env.sentry_dsn, env.sentry_environment)

# Settings for production environment
if APP_ENV == "production":
    # TODO: ICMSLST-2760 Add whitenoise static file compression.
    #       Note - commented out code below is for older versions of django.
    #       compression causes 50 error on server
    # STATICFILES_STORAGE='whitenoise.storage.CompressedManifestStaticFilesStorage'

    INSTALLED_APPS += [  # NOQA
        "django_audit_log_middleware",
    ]

    MIDDLEWARE += [  # NOQA
        "django_audit_log_middleware.AuditLogMiddleware",
    ]

    # Audit log middleware user field
    AUDIT_LOG_USER_FIELD = "username"

# Settings for non-production environments:
else:
    # Override secure cookies to use playwright in non-prod environments
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False

    # Used in tests to override the TEMPLATES setting.
    STRICT_TEMPLATES = copy.deepcopy(TEMPLATES)
    STRICT_TEMPLATES[0]["OPTIONS"].update({"undefined": jinja2.StrictUndefined})  # type: ignore[attr-defined]

    # Used to change one login auth level (remove 2FA in non-production)
    if env.gov_uk_one_login_authentication_level_override:
        GOV_UK_ONE_LOGIN_AUTHENTICATION_LEVEL = env.gov_uk_one_login_authentication_level_override  # type: ignore[assignment]

# Site URL management
CASEWORKER_SITE_URL = env.caseworker_site_url
IMPORTER_SITE_URL = env.importer_site_url
EXPORTER_SITE_URL = env.exporter_site_url

# CSP Settings

# CSP policies
CSP_DEFAULT_SRC = ("'self'",)

# JS tags with a src attribute can only be loaded from ICMS itself or the DBT Sentry instance
CSP_SCRIPT_SRC = (
    "'self'",
    "'unsafe-eval'",
    "sentry.ci.uktrade.digital",
    "cdnjs.cloudflare.com",
    "googletagmanager.com",
    "*.google-analytics.com",
)

# JS scripts can import other scripts, following the same rules as above
CSP_CONNECT_SRC = CSP_SCRIPT_SRC

# CSS elements with a src attribute can only be loaded from ICMS itself, google,  or inline, e.g. <style> tags
CSP_STYLE_SRC = (
    "'self'",
    "'unsafe-inline'",
    "fonts.gstatic.com",
    "fonts.googleapis.com",
    "googletagmanager.com",
)
# Fonts can only be loaded from ICMS itself, google, or data URIs
CSP_FONT_SRC = (
    "'self'",
    "data:",
    "fonts.gstatic.com",
)
# Images can only be loaded from ICMS itself, google, or data URIs
CSP_IMG_SRC = (
    "'self'",
    "data:",
    "googletagmanager.com",
    "fonts.gstatic.com",
)

# CSP meta-settings

# inline scripts without a src attribute must have a nonce attribute
CSP_INCLUDE_NONCE_IN = ["script-src"]

# if True, CSP violations are reported but not enforced
CSP_REPORT_ONLY = env.csp_report_only

# URL to send CSP violation reports to
CSP_REPORT_URI = env.csp_report_uri

# PDF signature certificate stuff
P12_SIGNATURE_BASE_64 = env.p12_signature_base_64
P12_SIGNATURE_PASSWORD = env.p12_signature_password

# Google Analytics stuff
GTM_ENABLED = env.gtm_enabled

GTM_CONTAINER_IDS = {
    "Manage import licences and export certificates": env.gtm_caseworker_container_id,
    "Apply for an export certificate": env.gtm_exporter_container_id,
    "Apply for an import licence": env.gtm_importer_container_id,
}
