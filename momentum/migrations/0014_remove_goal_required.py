# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0013_auto_20150727_1249'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='goal',
            name='required',
        ),
    ]
