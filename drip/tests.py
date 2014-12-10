from datetime import datetime, timedelta

from django.test import TestCase
from django.test.client import RequestFactory
from django.core.exceptions import ValidationError
from django.core.urlresolvers import resolve, reverse
from django.core import mail
from django.conf import settings
from django.utils import timezone

from drip.models import Drip, SentDrip, QuerySetRule
from drip.drips import DripBase, DripMessage
from drip.utils import get_user_model, unicode

from credits.models import Profile


class RulesTestCase(TestCase):
    def setUp(self):
        self.drip = Drip.objects.create(
            name='A Drip just for Rules',
            subject_template='Hello',
            body_html_template='KETTEHS ROCK!'
        )

    def test_valid_rule(self):
        rule = QuerySetRule(drip=self.drip, field_name='date_joined', lookup_type='lte', field_value='now-60 days')
        rule.clean()

    def test_bad_field_name(self):
        rule = QuerySetRule(drip=self.drip, field_name='date__joined', lookup_type='lte', field_value='now-60 days')
        self.assertRaises(ValidationError, rule.clean)

    def test_bad_field_value(self):
        rule = QuerySetRule(drip=self.drip, field_name='date_joined', lookup_type='lte', field_value='now-2 months')
        self.assertRaises(ValidationError, rule.clean)


class DripsTestCase(TestCase):

    def setUp(self):
        """
        Creates 20 users, half of which buy 25 credits a day,
        and the other half that does none.
        """
        self.User = get_user_model()

        start = timezone.now() - timedelta(hours=2)
        num_string = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth']

        for i, name in enumerate(num_string):
            user = self.User.objects.create(username='%s_25_credits_a_day' % name, email='%s@test.com' % name)
            self.User.objects.filter(id=user.id).update(date_joined=start - timedelta(days=i))

            profile = Profile.objects.get(user=user)
            profile.credits = i * 25
            profile.save()

        for i, name in enumerate(num_string):
            user = self.User.objects.create(username='%s_no_credits' % name, email='%s@test.com' % name)
            self.User.objects.filter(id=user.id).update(date_joined=start - timedelta(days=i))

    def test_users_exists(self):
        self.assertEqual(20, self.User.objects.all().count())

    def test_day_zero_users(self):
        start = timezone.now() - timedelta(days=1)
        end = timezone.now()
        self.assertEqual(2, self.User.objects.filter(date_joined__range=(start, end)).count())

    def test_day_two_users_active(self):
        start = timezone.now() - timedelta(days=3)
        end = timezone.now() - timedelta(days=2)
        self.assertEqual(1, self.User.objects.filter(date_joined__range=(start, end),
                                                profile__credits__gt=0).count())

    def test_day_two_users_inactive(self):
        start = timezone.now() - timedelta(days=3)
        end = timezone.now() - timedelta(days=2)
        self.assertEqual(1, self.User.objects.filter(date_joined__range=(start, end),
                                                profile__credits=0).count())

    def test_day_seven_users_active(self):
        start = timezone.now() - timedelta(days=8)
        end = timezone.now() - timedelta(days=7)
        self.assertEqual(1, self.User.objects.filter(date_joined__range=(start, end),
                                                profile__credits__gt=0).count())

    def test_day_seven_users_inactive(self):
        start = timezone.now() - timedelta(days=8)
        end = timezone.now() - timedelta(days=7)
        self.assertEqual(1, self.User.objects.filter(date_joined__range=(start, end),
                                                profile__credits=0).count())

    def test_day_fourteen_users_active(self):
        start = timezone.now() - timedelta(days=15)
        end = timezone.now() - timedelta(days=14)
        self.assertEqual(0, self.User.objects.filter(date_joined__range=(start, end),
                                                profile__credits__gt=0).count())

    def test_day_fourteen_users_inactive(self):
        start = timezone.now() - timedelta(days=15)
        end = timezone.now() - timedelta(days=14)
        self.assertEqual(0, self.User.objects.filter(date_joined__range=(start, end),
                                                profile__credits=0).count())

    ########################
    ### RELATION SNAGGER ###
    ########################

    def test_get_simple_fields(self):
        from drip.utils import get_simple_fields

        simple_fields = get_simple_fields(self.User)
        self.assertTrue(bool([sf for sf in simple_fields if 'profile' in sf[0]]))

    ##################
    ### TEST DRIPS ###
    ##################

    def test_backwards_drip_class(self):
        for drip in Drip.objects.all():
            self.assertTrue(issubclass(drip.drip.__class__, DripBase))

    def build_joined_date_drip(self, shift_one=7, shift_two=8):
        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='lt',
            field_value='now-{0} days'.format(shift_one)
        )
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='gte',
            field_value='now-{0} days'.format(shift_two)
        )
        return model_drip

    def test_custom_drip(self):
        """
        Test a simple
        """
        model_drip = self.build_joined_date_drip()
        drip = model_drip.drip

        # ensure we are starting from a blank slate
        self.assertEqual(2, drip.get_queryset().count()) # 2 people meet the criteria
        drip.prune()
        self.assertEqual(2, drip.get_queryset().count()) # no one is pruned, never sent before
        self.assertEqual(0, SentDrip.objects.count()) # confirm nothing sent before

        # send the drip
        drip.send()
        self.assertEqual(2, SentDrip.objects.count()) # got sent

        for sent in SentDrip.objects.all():
            self.assertIn('HELLO', sent.subject)
            self.assertIn('KETTEHS ROCK', sent.body)

        # subsequent runs reflect previous activity
        drip = Drip.objects.get(id=model_drip.id).drip
        self.assertEqual(2, drip.get_queryset().count()) # 2 people meet the criteria
        drip.prune()
        self.assertEqual(0, drip.get_queryset().count()) # everyone is pruned

    def test_custom_short_term_drip(self):
        model_drip = self.build_joined_date_drip(shift_one=3, shift_two=4)
        drip = model_drip.drip

        # ensure we are starting from a blank slate
        self.assertEqual(2, drip.get_queryset().count()) # 2 people meet the criteria


    def test_custom_date_range_walk(self):
        model_drip = self.build_joined_date_drip()
        drip = model_drip.drip

        # vanilla (now-8, now-7), past (now-8-3, now-7-3), future (now-8+1, now-7+1)
        for count, shifted_drip in zip([0, 2, 2, 2, 2], drip.walk(into_past=3, into_future=2)):
            self.assertEqual(count, shifted_drip.get_queryset().count())

        # no reason to change after a send...
        drip.send()
        drip = Drip.objects.get(id=model_drip.id).drip

        # vanilla (now-8, now-7), past (now-8-3, now-7-3), future (now-8+1, now-7+1)
        for count, shifted_drip in zip([0, 2, 2, 2, 2], drip.walk(into_past=3, into_future=2)):
            self.assertEqual(count, shifted_drip.get_queryset().count())

    def test_custom_drip_with_count(self):
        model_drip = self.build_joined_date_drip()
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='profile__credits',
            lookup_type='gte',
            field_value='5'
        )
        drip = model_drip.drip

        self.assertEqual(1, drip.get_queryset().count()) # 1 person meet the criteria

        for count, shifted_drip in zip([0, 1, 1, 1, 1], drip.walk(into_past=3, into_future=2)):
            self.assertEqual(count, shifted_drip.get_queryset().count())

    def test_exclude_and_include(self):
        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )

        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='profile__credits',
            lookup_type='gte',
            field_value='1'
        )
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='profile__credits',
            method_type='exclude',
            lookup_type='exact',
            field_value=100
        )
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='profile__credits',
            method_type='exclude',
            lookup_type='exact',
            field_value=125
        )
        self.assertEqual(7, model_drip.drip.get_queryset().count()) # 7 people meet the criteria

    def test_custom_drip_static_datetime(self):
        model_drip = self.build_joined_date_drip()
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='lte',
            field_value=(timezone.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
        )
        drip = model_drip.drip

        for count, shifted_drip in zip([0, 2, 2, 0, 0], drip.walk(into_past=3, into_future=2)):
            self.assertEqual(count, shifted_drip.get_queryset().count())

    def test_custom_drip_static_now_datetime(self):
        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='gte',
            field_value=(timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        )
        drip = model_drip.drip

        # catches "today and yesterday" users
        for count, shifted_drip in zip([4, 4, 4, 4, 4], drip.walk(into_past=3, into_future=3)):
            self.assertEqual(count, shifted_drip.get_queryset().count())

    def test_admin_timeline_prunes_user_output(self):
        """multiple users in timeline is confusing."""
        admin = self.User.objects.create(username='admin', email='admin@example.com')
        admin.is_staff=True
        admin.is_superuser=True
        admin.save()

        # create a drip campaign that will surely give us duplicates.
        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='gte',
            field_value=(timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        )

        # then get it's admin view.
        rf = RequestFactory()
        timeline_url = reverse('admin:drip_timeline', kwargs={
                                    'drip_id': model_drip.id,
                                    'into_past': 3,
                                    'into_future': 3})

        request = rf.get(timeline_url)
        request.user = admin

        match = resolve(timeline_url)

        response = match.func(request, *match.args, **match.kwargs)

        # check that our admin (not excluded from test) is shown once.
        self.assertEqual(unicode(response.content).count(admin.email), 1)


    ##################
    ### TEST M2M   ###
    ##################

    def test_annotated_field_name_property_no_count(self):
        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )

        qsr = QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='exact',
            field_value=2
        )
        self.assertEqual(qsr.annotated_field_name, 'date_joined')

    def test_annotated_field_name_property_with_count(self):

        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )

        qsr = QuerySetRule.objects.create(
            drip=model_drip,
            field_name='userprofile__user__groups__count',
            lookup_type='exact',
            field_value=2
        )

        self.assertEqual(qsr.annotated_field_name, 'num_userprofile_user_groups')

    def test_apply_annotations_no_count(self):

        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )

        qsr = QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='exact',
            field_value=2
        )

        qs = qsr.apply_any_annotation(None)

        self.assertEqual(qs, None)

    def test_apply_annotations_with_count(self):

        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )

        qsr = QuerySetRule.objects.create(
            drip=model_drip,
            field_name='profile__user__groups__count',
            lookup_type='exact',
            field_value=2
        )

        qs = qsr.apply_any_annotation(model_drip.drip.get_queryset())

        self.assertEqual(list(qs.query.aggregate_select.keys()), ['num_profile_user_groups'])

    def test_apply_multiple_rules_with_aggregation(self):

        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='KETTEHS ROCK!'
        )

        qsr = QuerySetRule.objects.create(
            drip=model_drip,
            field_name='profile__user__groups__count',
            lookup_type='exact',
            field_value='0'
        )

        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='gte',
            field_value=(timezone.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        )


        qsr.clean()
        qs = model_drip.drip.apply_queryset_rules(model_drip.drip.get_queryset())

        self.assertEqual(qs.count(), 4)


# Used by CustomMessagesTest
class PlainDripEmail(DripMessage):
    @property
    def message(self):
        if not self._message:
            email = mail.EmailMessage(self.subject, self.plain, self.from_email, [self.user.email])
            self._message = email
        return self._message


class CustomMessagesTest(TestCase):
    def setUp(self):
        self.User = get_user_model()

        self.old_msg_classes = getattr(settings, 'DRIP_MESSAGE_CLASSES', None)
        self.user = self.User.objects.create(username='customuser', email='custom@example.com')
        self.model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template='HELLO {{ user.username }}',
            body_html_template='<h2>This</h2> is an <b>example</b> html <strong>body</strong>.'
        )
        QuerySetRule.objects.create(
            drip=self.model_drip,
            field_name='id',
            lookup_type='exact',
            field_value=self.user.id,
        )

    def tearDown(self):
        if self.old_msg_classes is None:
            if hasattr(settings, 'DRIP_MESSAGE_CLASSES'):
                del settings.DRIP_MESSAGE_CLASSES
        else:
            settings.DRIP_MESSAGE_CLASSES = self.old_msg_classes

    def test_default_email(self):
        result = self.model_drip.drip.send()
        self.assertEqual(1, result)
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox.pop()
        self.assertIsInstance(email, mail.EmailMultiAlternatives)

    def test_custom_added_not_used(self):
        settings.DRIP_MESSAGE_CLASSES = {'plain': 'drip.tests.PlainDripEmail'}
        result = self.model_drip.drip.send()
        self.assertEqual(1, result)
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox.pop()
        # Since we did not specify custom class, default should be used.
        self.assertIsInstance(email, mail.EmailMultiAlternatives)

    def test_custom_added_and_used(self):
        settings.DRIP_MESSAGE_CLASSES = {'plain': 'drip.tests.PlainDripEmail'}
        self.model_drip.message_class = 'plain'
        self.model_drip.save()
        result = self.model_drip.drip.send()
        self.assertEqual(1, result)
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox.pop()
        # In this case we did specify the custom key, so message should be of custom type.
        self.assertIsInstance(email, mail.EmailMessage)

    def test_override_default(self):
        settings.DRIP_MESSAGE_CLASSES = {'default': 'drip.tests.PlainDripEmail'}
        result = self.model_drip.drip.send()
        self.assertEqual(1, result)
        self.assertEqual(1, len(mail.outbox))
        email = mail.outbox.pop()
        self.assertIsInstance(email, mail.EmailMessage)
