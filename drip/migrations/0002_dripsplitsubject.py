# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('drip', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DripSplitSubject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=150)),
                ('enabled', models.BooleanField(default=True)),
                ('drip', models.ForeignKey(related_name='split_test_subjects', to='drip.Drip')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
