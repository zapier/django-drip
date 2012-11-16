from datetime import datetime, timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from drip.models import Drip, SentDrip, QuerySetRule
from drip.drips import DripBase
from django.core.mail import EmailMultiAlternatives


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
        start = datetime.now() - timedelta(hours=2)
        num_string = ['first','second','third','fourth','fifth','sixth','seventh','eighth','ninth','tenth']

        for i, name in enumerate(num_string):
            user = User.objects.create(username='%s_25_credits_a_day' % name, email='%s@test.com' % name)
            User.objects.filter(id=user.id).update(date_joined=start - timedelta(days=i))

            profile = user.get_profile()
            profile.credits = i * 25
            profile.save()

        for i, name in enumerate(num_string):
            user = User.objects.create(username='%s_no_credits' % name, email='%s@test.com' % name)
            User.objects.filter(id=user.id).update(date_joined=start - timedelta(days=i))


    def test_users_exists(self):
        self.assertEqual(20, User.objects.all().count())

    def test_day_zero_users(self):
        start = datetime.now() - timedelta(days=1)
        end = datetime.now()
        self.assertEqual(2, User.objects.filter(date_joined__range=(start, end)).count())

    def test_day_two_users_active(self):
        start = datetime.now() - timedelta(days=3)
        end = datetime.now() - timedelta(days=2)
        self.assertEqual(1, User.objects.filter(date_joined__range=(start, end),
                                                profile__credits__gt=0).count())

    def test_day_two_users_inactive(self):
        start = datetime.now() - timedelta(days=3)
        end = datetime.now() - timedelta(days=2)
        self.assertEqual(1, User.objects.filter(date_joined__range=(start, end),
                                                profile__credits=0).count())

    def test_day_seven_users_active(self):
        start = datetime.now() - timedelta(days=8)
        end = datetime.now() - timedelta(days=7)
        self.assertEqual(1, User.objects.filter(date_joined__range=(start, end),
                                                profile__credits__gt=0).count())

    def test_day_seven_users_inactive(self):
        start = datetime.now() - timedelta(days=8)
        end = datetime.now() - timedelta(days=7)
        self.assertEqual(1, User.objects.filter(date_joined__range=(start, end),
                                                profile__credits=0).count())

    def test_day_fourteen_users_active(self):
        start = datetime.now() - timedelta(days=15)
        end = datetime.now() - timedelta(days=14)
        self.assertEqual(0, User.objects.filter(date_joined__range=(start, end),
                                                profile__credits__gt=0).count())

    def test_day_fourteen_users_inactive(self):
        start = datetime.now() - timedelta(days=15)
        end = datetime.now() - timedelta(days=14)
        self.assertEqual(0, User.objects.filter(date_joined__range=(start, end),
                                                profile__credits=0).count())

    ########################
    ### RELATION SNAGGER ###
    ########################

    def test_get_simple_fields(self):
        from drip.utils import get_simple_fields

        simple_fields = get_simple_fields(User)
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
            self.assertEquals(count, shifted_drip.get_queryset().count())

        # no reason to change after a send...
        drip.send()
        drip = Drip.objects.get(id=model_drip.id).drip

        # vanilla (now-8, now-7), past (now-8-3, now-7-3), future (now-8+1, now-7+1)
        for count, shifted_drip in zip([0, 2, 2, 2, 2], drip.walk(into_past=3, into_future=2)):
            self.assertEquals(count, shifted_drip.get_queryset().count())

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
            self.assertEquals(count, shifted_drip.get_queryset().count())

    def test_custom_drip_static_datetime(self):
        model_drip = self.build_joined_date_drip()
        QuerySetRule.objects.create(
            drip=model_drip,
            field_name='date_joined',
            lookup_type='lte',
            field_value=(datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d %H:%M:%S')
        )
        drip = model_drip.drip

        for count, shifted_drip in zip([0, 2, 2, 0, 0], drip.walk(into_past=3, into_future=2)):
            self.assertEquals(count, shifted_drip.get_queryset().count())

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
            field_value=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d 00:00:00')
        )
        drip = model_drip.drip

        # catches "today and yesterday" users
        for count, shifted_drip in zip([4, 4, 4, 4, 4], drip.walk(into_past=3, into_future=3)):
            self.assertEquals(count, shifted_drip.get_queryset().count())

    def test_build_email(self):
        body_html_template = '<h2>This</h2> is an <b>example</b> html <strong>body</strong> for {{ user.username }}.'
        subject_template = 'HELLO {{ user.username }}'
        model_drip = Drip.objects.create(
            name='A Custom Week Ago',
            subject_template=subject_template,
            body_html_template=body_html_template
        )

        #: grabs base drip instance
        drip = model_drip.drip
        user = User.objects.get(id=1)
        email = drip.build_email(user, send=True)

        self.assertIsInstance(email, EmailMultiAlternatives)
        expected_result_body = body_html_template.replace("{{ user.username }}", user.username)
        expected_result_subject = subject_template.replace("{{ user.username }}", user.username)
        from django.core import mail
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, expected_result_subject)
        # It's rather ugly to retrieve the HTML version from the email (below)
        html_body = mail.outbox[0].message().get_payload()[-1].get_payload()    # Basically, get the first captured message, get it's message object, grab the payload of the envelope which returns [text/plain, text/html] attachments (so grab index -1) and then call get_payload on that message to get the body
        self.assertEqual(html_body, expected_result_body)        

