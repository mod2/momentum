# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0005_auto_20150120_2230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='target_amount',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
