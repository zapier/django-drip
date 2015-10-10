# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drip', '0002_dripsplitsubject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dripsplitsubject',
            name='drip',
        ),
        migrations.AlterField(
            model_name='drip',
            name='from_email',
            field=models.EmailField(help_text=b'Set a custom from email.', max_length=254, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='sentdrip',
            name='from_email',
            field=models.EmailField(default=None, max_length=254, null=True),
        ),
        migrations.DeleteModel(
            name='DripSplitSubject',
        ),
    ]
