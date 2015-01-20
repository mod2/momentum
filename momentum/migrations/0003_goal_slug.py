# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0002_auto_20150120_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='slug',
            field=models.CharField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
    ]
