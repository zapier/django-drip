Django Drip
====================

[![Build Status](https://secure.travis-ci.org/zapier/django-drip.png)](http://travis-ci.org/zapier/django-drip)

Drip campaigns are pre-written sets of emails sent to customers or prospects over time. Django Drips lets you use the admin to manage drip campaign emails using querysets on Django's User model.

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

### Custom Sender

If you want to send messages different from the default sender (SMTP),
you can create a custom sender class that inherits from `SenderBase`. For example:

```python
from drip.models import SenderBase

class CustomSender(SenderBase):
    # drip is the drip.drips.DripBase object which gives access to
    # from_address and from_address_name
    def send_message(self, drip, user, subject, body, plain):
        # Custom sending logic (SMS, in app messaging, snail mail, etc.)
        ...
        # Return a boolean indicating if the message was sent or not
```

After adding this table to the database using syncdb or a south migration, you
will need to create an object of this type:

```shell
$ python manage.py shell
>>> from exampleapp.models import CustomSender
>>> sender = CustomSender()
>>> sender.name = 'My Custom Sender'
>>> sender.save()
```

Now when you create a `Drip` in the django admin you will have the option of
selecting your own custom sender. When these `Drip`s go out, django drip will
send the message with your custom sender instead of the built-in method.

-------------------

![what the admin looks like](https://raw.github.com/zapier/django-drip/master/docs/images/drip-example.png)
![what the admin looks like for the timeline](https://raw.github.com/zapier/django-drip/master/docs/images/view-timeline.png)
