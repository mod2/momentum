# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0010_target_data_migration'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='required',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
