
# MUST SPECIFY TO MAKE USE OF DJANGO DRIP
DRIP_FROM_EMAIL = ''

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',

    'drip',

    # testing only
    'credits',
)

AUTH_PROFILE_MODULE = 'credits.Profile'

