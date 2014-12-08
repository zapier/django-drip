from datetime import datetime, timedelta

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from drip.utils import get_user_model

# just using this to parse, but totally insane package naming...
# https://bitbucket.org/schinckel/django-timedelta-field/
import timedelta as djangotimedelta


class Drip(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)

    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Drip Name',
        help_text='A unique name for this drip.')

    enabled = models.BooleanField(default=False)

    from_email = models.EmailField(null=True, blank=True,
        help_text='Set a custom from email.')
    from_email_name = models.CharField(max_length=150, null=True, blank=True,
        help_text="Set a name for a custom from email.")
    subject_template = models.TextField(null=True, blank=True)
    body_html_template = models.TextField(null=True, blank=True,
        help_text='You will have settings and user in the context.')
    message_class = models.CharField(max_length=120, blank=True, default='default')

    @property
    def drip(self):
        from drip.drips import DripBase

        drip = DripBase(drip_model=self,
                        name=self.name,
                        from_email=self.from_email if self.from_email else None,
                        from_email_name=self.from_email_name if self.from_email_name else None,
                        subject_template=self.subject_template if self.subject_template else None,
                        body_template=self.body_html_template if self.body_html_template else None)
        return drip

    def __unicode__(self):
        return self.name


class SentDrip(models.Model):
    """
    Keeps a record of all sent drips.
    """
    date = models.DateTimeField(auto_now_add=True)

    drip = models.ForeignKey('drip.Drip', related_name='sent_drips')
    user = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), related_name='sent_drips')

    subject = models.TextField()
    body = models.TextField()
    from_email = models.EmailField(
        null=True, default=None # For south so that it can migrate existing rows.
    )
    from_email_name = models.CharField(max_length=150,
        null=True, default=None # For south so that it can migrate existing rows.
    )



METHOD_TYPES = (
    ('filter', 'Filter'),
    ('exclude', 'Exclude'),
)

LOOKUP_TYPES = (
    ('exact', 'exactly'),
    ('iexact', 'exactly (case insensitive)'),
    ('contains', 'contains'),
    ('icontains', 'contains (case insensitive)'),
    ('regex', 'regex'),
    ('iregex', 'contains (case insensitive)'),
    ('gt', 'greater than'),
    ('gte', 'greater than or equal to'),
    ('lt', 'lesser than'),
    ('lte', 'lesser than or equal to'),
    ('startswith', 'starts with'),
    ('endswith', 'starts with'),
    ('istartswith', 'ends with (case insensitive)'),
    ('iendswith', 'ends with (case insensitive)'),
)

class QuerySetRule(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    lastchanged = models.DateTimeField(auto_now=True)

    drip = models.ForeignKey(Drip, related_name='queryset_rules')

    method_type = models.CharField(max_length=12, default='filter', choices=METHOD_TYPES)
    field_name = models.CharField(max_length=128, verbose_name='Field name off User')
    lookup_type = models.CharField(max_length=12, default='exact', choices=LOOKUP_TYPES)

    field_value = models.CharField(max_length=255,
        help_text=('Can be anything from a number, to a string. Or, do ' +
                   '`now-7 days` or `now+3 days` for fancy timedelta.'))

    def clean(self):
        User = get_user_model()
        try:
            self.apply(User.objects.all())
        except Exception as e:
            raise ValidationError(
                '%s raised trying to apply rule: %s' % (type(e).__name__, e))

    def apply(self, qs, now=datetime.now):
        # Support Count() as m2m__count
        field_name = self.field_name
        if field_name.endswith('__count'):
            agg, _, _ = self.field_name.rpartition('__')
            field_name = 'num_%s' % agg
            qs = qs.annotate(**{field_name: models.Count(agg)})

        field_name = '__'.join([field_name, self.lookup_type])
        field_value = self.field_value

        # set time deltas and dates
        if field_value.startswith('now-'):
            field_value = self.field_value.replace('now-', '')
            delta = djangotimedelta.parse(field_value)
            field_value = now() - delta
        elif field_value.startswith('now+'):
            field_value = self.field_value.replace('now+', '')
            delta = djangotimedelta.parse(field_value)
            field_value = now() + delta

        # set booleans
        if field_value == 'True':
            field_value = True
        if field_value == 'False':
            field_value = False

        kwargs = {field_name: field_value}

        if self.method_type == 'filter':
            return qs.filter(**kwargs)
        elif self.method_type == 'exclude':
            return qs.exclude(**kwargs)

        # catch as default
        return qs.filter(**kwargs)
