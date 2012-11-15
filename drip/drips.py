from django.conf import settings
from datetime import datetime

from django.contrib.auth.models import User
from django.template import Context, Template
from drip.models import SentDrip
from django.core.mail import EmailMultiAlternatives


class DripBase(object):
    """
    A base object for defining a Drip.

    You can extend this manually, or you can create full querysets
    and templates from the admin.
    """
    #: needs a unique name
    name = None
    subject_template = None
    body_template = None

    def __init__(self, drip_model, *args, **kwargs):
        self.drip_model = drip_model

        self.name = kwargs.pop('name', self.name)

        self.subject_template = kwargs.pop('subject_template', self.subject_template)
        self.body_template = kwargs.pop('body_template', self.body_template)

        if not self.name:
            raise AttributeError('You must define a name.')

        self.now_shift_kwargs = kwargs.get('now_shift_kwargs', {})


    #########################
    ### DATE MANIPULATION ###
    #########################

    def now(self):
        """
        This allows us to override what we consider "now", making it easy
        to build timelines of who gets what when.
        """
        return datetime.now() + self.timedelta(**self.now_shift_kwargs)

    def timedelta(self, *a, **kw):
        """
        If needed, this allows us the ability to manipuate the slicing of time.
        """
        from datetime import timedelta
        return timedelta(*a, **kw)

    def walk(self, into_past=0, into_future=0):
        """
        Walk over a date range and create new instances of self with new ranges.
        """
        walked_range = []
        for shift in range(-into_past, into_future):
            kwargs = dict(drip_model=self.drip_model,
                          name=self.name,
                          now_shift_kwargs={'days': shift})
            walked_range.append(self.__class__(**kwargs))
        return walked_range

    def apply_queryset_rules(self, qs):
        for queryset_rule in self.drip_model.queryset_rules.all():
            qs = queryset_rule.apply(qs, now=self.now)
        return qs

    ##################
    ### MANAGEMENT ###
    ##################

    def get_queryset(self):
        try:
            return self._queryset
        except AttributeError:
            self._queryset = self.apply_queryset_rules(self.queryset())\
                                 .distinct()
            return self._queryset

    def run(self):
        """
        Get the queryset, prune sent people, and send it.
        """
        if not self.drip_model.enabled:
            return None

        self.prune()
        count = self.send()

        return count

    def prune(self):
        """
        Do an exclude for all Users who have a SentDrip already.
        """
        target_user_ids = self.get_queryset().values_list('id', flat=True)
        exclude_user_ids = SentDrip.objects.filter(date__lt=datetime.now(),
                                                   drip=self.drip_model,
                                                   user__id__in=target_user_ids)\
                                           .values_list('user_id', flat=True)
        self._queryset = self.get_queryset().exclude(id__in=exclude_user_ids)

    def build_email(self, user, send=False):
        """
        Creates Email instance and optionally sends to user.
        """
        from django.utils.html import strip_tags

        from_email = getattr(settings, 'DRIP_FROM_EMAIL', settings.EMAIL_HOST_USER)

        context = Context({'user': user})
        subject = Template(self.subject_template).render(context)
        body = Template(self.body_template).render(context)
        plain = strip_tags(body)

        email = EmailMultiAlternatives(subject, plain, from_email, [user.email])

        # check if there are html tags in the rendered template
        if len(plain) != len(body):
            email.attach_alternative(body, 'text/html')

        if send:
            sd = SentDrip.objects.create(
                drip=self.drip_model,
                user=user,
                subject=subject,
                body=body
            )
            email.send()

        return email

    def send(self):
        """
        Send the email to each user on the queryset.

        Add that user to the SentDrip.

        Returns a list of created SentDrips.
        """

        count = 0
        for user in self.get_queryset():
            msg = self.build_email(user, send=True)
            count += 1

        return count


    ####################
    ### USER DEFINED ###
    ####################

    def queryset(self):
        """
        Returns a queryset of auth.User who meet the
        criteria of the drip.

        Alternatively, you could create Drips on the fly
        using a queryset builder from the admin interface...
        """
        return User.objects
