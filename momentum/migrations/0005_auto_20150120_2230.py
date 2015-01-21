# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0004_remove_entry_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entry',
            name='time',
            field=models.DateTimeField(),
        ),
    ]
