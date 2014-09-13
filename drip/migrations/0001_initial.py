# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Drip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('lastchanged', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(help_text=b'A unique name for this drip.', unique=True, max_length=255, verbose_name=b'Drip Name')),
                ('enabled', models.BooleanField(default=False)),
                ('from_email', models.EmailField(help_text=b'Set a custom from email.', max_length=75, null=True, blank=True)),
                ('from_email_name', models.CharField(help_text=b'Set a name for a custom from email.', max_length=150, null=True, blank=True)),
                ('subject_template', models.TextField(null=True, blank=True)),
                ('body_html_template', models.TextField(help_text=b'You will have settings and user in the context.', null=True, blank=True)),
                ('message_class', models.CharField(default=b'default', max_length=120, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuerySetRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('lastchanged', models.DateTimeField(auto_now=True)),
                ('method_type', models.CharField(default=b'filter', max_length=12, choices=[(b'filter', b'Filter'), (b'exclude', b'Exclude')])),
                ('field_name', models.CharField(max_length=128, verbose_name=b'Field name off User')),
                ('lookup_type', models.CharField(default=b'exact', max_length=12, choices=[(b'exact', b'exactly'), (b'iexact', b'exactly (case insensitive)'), (b'contains', b'contains'), (b'icontains', b'contains (case insensitive)'), (b'regex', b'regex'), (b'iregex', b'contains (case insensitive)'), (b'gt', b'greater than'), (b'gte', b'greater than or equal to'), (b'lt', b'lesser than'), (b'lte', b'lesser than or equal to'), (b'startswith', b'starts with'), (b'endswith', b'starts with'), (b'istartswith', b'ends with (case insensitive)'), (b'iendswith', b'ends with (case insensitive)')])),
                ('field_value', models.CharField(help_text=b'Can be anything from a number, to a string. Or, do `now-7 days` or `now+3 days` for fancy timedelta.', max_length=255)),
                ('drip', models.ForeignKey(related_name=b'queryset_rules', to='drip.Drip')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SentDrip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('subject', models.TextField()),
                ('body', models.TextField()),
                ('from_email', models.EmailField(default=None, max_length=75, null=True)),
                ('from_email_name', models.CharField(default=None, max_length=150, null=True)),
                ('drip', models.ForeignKey(related_name=b'sent_drips', to='drip.Drip')),
                ('user', models.ForeignKey(related_name=b'sent_drips', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
