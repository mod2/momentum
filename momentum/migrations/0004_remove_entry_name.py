# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0003_goal_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='name',
        ),
    ]
