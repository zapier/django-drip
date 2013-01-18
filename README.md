Django Drip
====================

[![Build Status](https://secure.travis-ci.org/zapier/django-drip.png)](http://travis-ci.org/zapier/django-drip)

Drip campaigns are pre-written sets of emails sent to customers or prospects over time. Django Drips lets you use the admin to manage drip campaign emails using querysets on Django's User model.

We wrote this specifically to scratch an itch at our startup [Zapier](https://zapier.com/z/qO/). It currently runs all of our drip campaigns.

[Read the docs](https://django-drip.readthedocs.org/en/latest/) or [check out a demo](http://djangodrip.com/).

### Installing:

We highly recommend using pip to install *django-drip*, the packages are regularly updated 
with stable releases:

```
pip install django-drip
```

Next, you'll want to add `drip` to your `INSTALLED_APPS` in settings.py.

```python
INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.comments',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',

    # Your favorite apps

    'drip',
)
```

Don't forget to add `DRIP_FROM_EMAIL` to settings.py, or else we will fall back to `EMAIL_HOST_USER`.

Finally, be sure to run `python manage.py syncdb` or `python manage.py migrate drip` to set up
the necessary database tables.

```
python manage.py syncdb
# or...
python manage.py migrate drip
```
-------------------

![what the admin looks like](https://raw.github.com/zapier/django-drip/master/docs/images/drip-example.png)
![what the admin looks like for the timeline](https://raw.github.com/zapier/django-drip/master/docs/images/view-timeline.png)
