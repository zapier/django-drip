SECRET_KEY="whatever"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    },
}

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.admin',
    'django.contrib.sessions',
    'django.contrib.contenttypes',
    'django.contrib.staticfiles',
    'drip',
    'tests',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

USE_TZ = True
TIME_ZONE = 'UTC'

AUTH_PROFILE_MODULE = 'tests.Profile'

ROOT_URLCONF = 'tests.urls'

STATIC_URL = '/static/'
STATICFILES_DIRS = ()

DRIP_FROM_EMAIL = ''