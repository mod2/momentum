# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0006_auto_20150315_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='slug',
            field=autoslug.fields.AutoSlugField(editable=False),
        ),
    ]
