# -*- coding: utf-8 -*-
# Django settings

import os.path
from os import environ
import environ as envmax

env = envmax.Env()

from django.template.defaultfilters import slugify

PROJECT_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

DEBUG = True

# serve media through the staticfiles app.
SERVE_MEDIA = DEBUG

INTERNAL_IPS = [
    "127.0.0.1",
]

ADMINS = [
    ("Krzysztof Szumny", "noisy.pl@gmail.com"),
]

MANAGERS = ADMINS

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "US/Eastern"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_ROOT, "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# Absolute path to the directory that holds static files like app media.
# Example: "/home/media/media.lawrence.com/apps/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, "collected_static")

# URL that handles the static files like app media.
# Example: "http://media.lawrence.com"
STATIC_URL = "/static/"

# Additional directories which hold static files
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, "static"),
]

# Use the default admin media prefix, which is...
#ADMIN_MEDIA_PREFIX = "/static/admin/"


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dj_pagination.middleware.PaginationMiddleware',
]

TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            os.path.join(PROJECT_ROOT, "templates"),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
                "package.context_processors.used_packages_list",
                "package.context_processors.deployment",
                "grid.context_processors.grid_headers",
                "core.context_processors.current_path",
                "profiles.context_processors.lazy_profile",
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                "core.context_processors.core_values",
            ],
        },
    },
]

PROJECT_APPS = [
    "grid",
    'core',
    "homepage",
    "package",
    "profiles",
    "feeds",
    "searchv2",
    "apiv3",
    "steemconnect",
]

PREREQ_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.humanize",
    "django.contrib.staticfiles",

    # external
    "crispy_forms",
    "dj_pagination",
    "django_extensions",
    "reversion",
    "webstack_django_sorting",
    #"django_modeler",

    'social_django',
    'floppyforms',
    'rest_framework',

]

INSTALLED_APPS = PREREQ_APPS + PROJECT_APPS


MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

ABSOLUTE_URL_OVERRIDES = {
    "auth.user": lambda o: "/profiles/profile/%s/" % o.username,
}

AUTH_PROFILE_MODULE = "profiles.Profile"

LOGIN_URL = "/auth/login/github/"
LOGIN_REDIRECT_URLNAME = "home"

EMAIL_CONFIRMATION_DAYS = 2
EMAIL_DEBUG = DEBUG

CACHE_TIMEOUT = 60 * 60

ROOT_URLCONF = "urls"

SECRET_KEY = "CHANGEME"

URCHIN_ID = ""

DEFAULT_FROM_EMAIL = 'Steem Projects <steemprojects-noreply@steemprojects.com>'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[Steem Projects] '
try:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'smtp.sendgrid.net'
    EMAIL_HOST_PASSWORD = os.environ['SENDGRID_PASSWORD']
    EMAIL_HOST_USER = os.environ['SENDGRID_USERNAME']
    EMAIL_PORT = 587
    SERVER_EMAIL = 'info@cartwheelweb.com'
    EMAIL_USE_TLS = True
    DEBUG = False
except Exception as e:
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

EMAIL_SUBJECT_PREFIX = '[Cartwheel Web]'

EMAIL_SENDER_DOMAIN = env('MAILGUN_SENDER_DOMAIN')

DEBUG_TOOLBAR_CONFIG = {
    "INTERCEPT_REDIRECTS": False,
}

PACKAGINATOR_HELP_TEXT = {
    "REPO_URL": "Enter your project repo hosting URL here. Example: https://github.com/opencomparison/opencomparison",
    "PYPI_URL": "<strong>Leave this blank if this package does not have a PyPI release.</strong> What PyPI uses to index your package. Example: django-uni-form",
}

PACKAGINATOR_SEARCH_PREFIX = "django"

# if set to False any auth user can add/modify packages
# only django admins can delete
RESTRICT_PACKAGE_EDITORS = True

# if set to False  any auth user can add/modify grids
# only django admins can delete
RESTRICT_GRID_EDITORS = True


LOCAL_INSTALLED_APPS = []
SUPPORTED_REPO = []

########## GITHUB
GITHUB_API_SECRET = environ.get('GITHUB_API_SECRET')
GITHUB_APP_ID = environ.get('GITHUB_APP_ID')
GITHUB_TOKEN = environ.get('GITHUB_TOKEN')
GITHUB_USERNAME = environ.get('GITHUB_USERNAME')

########## STEEMCONNECT
STEEMCONNECT_APP_ID = environ.get('STEEMCONNECT_APP_ID')
STEEMCONNECT_APP_SECRET = environ.get('STEEMCONNECT_APP_SECRET')

########################## Site specific stuff
FRAMEWORK_TITLE = "Steem"
SITE_TITLE = "Steem Projects"

if LOCAL_INSTALLED_APPS:
    INSTALLED_APPS.extend(LOCAL_INSTALLED_APPS)

SUPPORTED_REPO.extend(["bitbucket", "github"])


AUTHENTICATION_BACKENDS = (
    'social_core.backends.github.GithubOAuth2',
    'social_core.backends.facebook.FacebookOAuth2',
    'steemconnect.steemconnect.SteemConnectOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GITHUB_KEY = GITHUB_APP_ID
SOCIAL_AUTH_GITHUB_SECRET = GITHUB_API_SECRET
SOCIAL_AUTH_GITHUB_SCOPE = ['user:email']

FACEBOOK_APP_ID = environ.get('FACEBOOK_APP_ID')
FACEBOOK_APP_SECRET = environ.get('FACEBOOK_APP_SECRET')
SOCIAL_AUTH_FACEBOOK_KEY = FACEBOOK_APP_ID
SOCIAL_AUTH_FACEBOOK_SECRET = FACEBOOK_APP_SECRET
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {
    'fields': 'id, name, email'
}
SOCIAL_AUTH_STEEMCONNECT_KEY = STEEMCONNECT_APP_ID
SOCIAL_AUTH_STEEMCONNECT_SECRET = STEEMCONNECT_APP_SECRET

SOCIAL_AUTH_STEEMCONNECT_SCOPE = ['vote', 'comment']

SOCIAL_AUTH_ENABLED_BACKENDS = ('github', 'facebook', 'steemconnect')
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'associate_complete'
SOCIAL_AUTH_DEFAULT_USERNAME = lambda u: slugify(u)
SOCIAL_AUTH_CHANGE_SIGNAL_ONLY = True
SOCIAL_AUTH_REDIRECT_IS_HTTPS = True
SOCIAL_AUTH_ADMIN_USER_SEARCH_FIELDS = ['username', 'first_name', 'email']

SOCIAL_AUTH_PIPELINE = (
    # Get the information we can about the user and return it in a simple
    # format to create the user instance later. On some cases the details are
    # already part of the auth response from the provider, but sometimes this
    # could hit a provider API.
    'social_core.pipeline.social_auth.social_details',

    # Get the social uid from whichever service we're authing thru. The uid is
    # the unique identifier of the given user in the provider.
    'social_core.pipeline.social_auth.social_uid',

    # Verifies that the current auth process is valid within the current
    # project, this is where emails and domains whitelists are applied (if
    # defined).
    'social_core.pipeline.social_auth.auth_allowed',

    # Checks if the current social-account is already associated in the site.
    'social_core.pipeline.social_auth.social_user',

    # CUSTOM PIPELINE
    'steemconnect.pipeline.require_email',

    # Make up a username for this person, appends a random string at the end if
    # there's any collision.
    'social_core.pipeline.user.get_username',

    # Send a validation email to the user to verify its email address.
    'social_core.pipeline.mail.mail_validation',

    # Associates the current social details with another user account with
    # a similar email address. Disabled by default.
    'social_core.pipeline.social_auth.associate_by_email',

    # Create a user account if we haven't found one yet.
    'social_core.pipeline.user.create_user',

    # Create the record that associates the social account with the user.
    'social_core.pipeline.social_auth.associate_user',

    # Populate the extra_data field in the social record with the values
    # specified by settings (and the default ones like access_token, etc).
    'social_core.pipeline.social_auth.load_extra_data',

    'profiles.views.save_profile_pipeline',

    # Update the user record with any changed info from the auth service.
    'social_core.pipeline.user.user_details',
)

SOCIAL_AUTH_EMAIL_VALIDATION_FUNCTION = 'steemconnect.mail.send_validation'
SOCIAL_AUTH_EMAIL_VALIDATION_URL = '/steemconnect/email-sent/'
SOCIAL_AUTH_STEEMCONNECT_FORCE_EMAIL_VALIDATION = True
VALIDATION_EMAIL_SENDER = environ.get('VALIDATION_EMAIL_SENDER')

LOGIN_REDIRECT_URL = '/'

DATABASES = {

    "default": env.db("DATABASE_URL")
}


WSGI_APPLICATION = 'wsgi.application'

if DEBUG:

    #MIDDLEWARE.append('debug_toolbar.middleware.DebugToolbarMiddleware')
    INSTALLED_APPS += ('debug_toolbar',)

    INTERNAL_IPS = ('127.0.0.1',)

    DEBUG_TOOLBAR_CONFIG = {
        'INTERCEPT_REDIRECTS': False,
        'SHOW_TEMPLATE_CONTEXT': True,
    }
    x = 1

ADMIN_URL_BASE = environ.get('ADMIN_URL_BASE', r"^admin/")

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': True,
#     'formatters': {
#         'standard': {
#             'format': "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s",
#             'datefmt': "%d/%b/%Y %H:%M:%S"
#         },
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logutils.colorize.ColorizingStreamHandler',
#             'formatter': 'standard'
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'include_html': True,
#         },
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['console', ],
#             'propagate': True,
#             'level': 'ERROR',
#         },
#         'django.request': {

#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         '': {
#             'handlers': ['console', ],
#             'level': os.environ.get('DEBUG_LEVEL', 'ERROR'),
#         },
#     }
# }


URL_REGEX_GITHUB = r'(?:http|https|git)://github.com/[^/]*/([^/]*)/{0,1}'

########### redis setup

# import redis
# from rq import Worker, Queue, Connection

########### end redis setup

########### crispy_forms setup
CRISPY_TEMPLATE_PACK = "bootstrap3"
########### end crispy_forms setup


########### LICENSES from PyPI
LICENSES = """License :: Aladdin Free Public License (AFPL)
License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
License :: DFSG approved
License :: Eiffel Forum License (EFL)
License :: Free For Educational Use
License :: Free For Home Use
License :: Free for non-commercial use
License :: Freely Distributable
License :: Free To Use But Restricted
License :: Freeware
License :: Netscape Public License (NPL)
License :: Nokia Open Source License (NOKOS)
License :: OSI Approved
License :: OSI Approved :: Academic Free License (AFL)
License :: OSI Approved :: Apache Software License
License :: OSI Approved :: Apple Public Source License
License :: OSI Approved :: Artistic License
License :: OSI Approved :: Attribution Assurance License
License :: OSI Approved :: BSD License
License :: OSI Approved :: Common Public License
License :: OSI Approved :: Eiffel Forum License
License :: OSI Approved :: European Union Public Licence 1.0 (EUPL 1.0)
License :: OSI Approved :: European Union Public Licence 1.1 (EUPL 1.1)
License :: OSI Approved :: GNU Affero General Public License v3
License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)
License :: OSI Approved :: GNU Free Documentation License (FDL)
License :: OSI Approved :: GNU General Public License (GPL)
License :: OSI Approved :: GNU General Public License v2 (GPLv2)
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)
License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)
License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)
License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)
License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)
License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)
License :: OSI Approved :: IBM Public License
License :: OSI Approved :: Intel Open Source License
License :: OSI Approved :: ISC License (ISCL)
License :: OSI Approved :: Jabber Open Source License
License :: OSI Approved :: MIT License
License :: OSI Approved :: MITRE Collaborative Virtual Workspace License (CVW)
License :: OSI Approved :: Motosoto License
License :: OSI Approved :: Mozilla Public License 1.0 (MPL)
License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)
License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)
License :: OSI Approved :: Nethack General Public License
License :: OSI Approved :: Nokia Open Source License
License :: OSI Approved :: Open Group Test Suite License
License :: OSI Approved :: Python License (CNRI Python License)
License :: OSI Approved :: Python Software Foundation License
License :: OSI Approved :: Qt Public License (QPL)
License :: OSI Approved :: Ricoh Source Code Public License
License :: OSI Approved :: Sleepycat License
License :: OSI Approved :: Sun Industry Standards Source License (SISSL)
License :: OSI Approved :: Sun Public License
License :: OSI Approved :: University of Illinois/NCSA Open Source License
License :: OSI Approved :: Vovida Software License 1.0
License :: OSI Approved :: W3C License
License :: OSI Approved :: X.Net License
License :: OSI Approved :: zlib/libpng License
License :: OSI Approved :: Zope Public License
License :: Other/Proprietary License
License :: Public Domain
License :: Repoze Public License""".splitlines()
########### End LICENSES from PyPI

########### SEKURITY
ALLOWED_HOSTS = ["*"]

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20
}

import datetime
DEPLOYMENT_DATATIME = environ.get('DEPLOYMENT_DATATIME', datetime.datetime.utcnow().isoformat())
