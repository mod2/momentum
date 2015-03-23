# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0008_auto_20150320_2059'),
    ]

    operations = [
        migrations.AddField(
            model_name='entry',
            name='target_amount',
            field=models.PositiveSmallIntegerField(default=0, null=True, blank=True),
            preserve_default=True,
        ),
    ]
