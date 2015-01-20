# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('momentum', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'verbose_name_plural': 'entries'},
        ),
        migrations.AddField(
            model_name='goal',
            name='owner',
            field=models.ForeignKey(related_name='goals', default=0, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='goal',
            name='priority',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
