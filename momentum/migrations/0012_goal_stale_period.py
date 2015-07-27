# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0011_goal_required'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='stale_period',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
