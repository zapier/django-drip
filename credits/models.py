from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    For testing, track the number of "credits".
    """
    user = models.OneToOneField('auth.User', related_name='profile')
    credits = models.PositiveIntegerField(default=0)


def user_post_save(sender, instance, created, raw, **kwargs):
    if created:
        Profile.objects.create(user=instance)
models.signals.post_save.connect(user_post_save, sender=User)
