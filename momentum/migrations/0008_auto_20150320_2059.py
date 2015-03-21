# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0007_auto_20150315_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goal',
            name='owner',
            field=models.ForeignKey(related_name='goals', default=1, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='goal',
            name='period',
            field=models.CharField(default='day', max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='goal',
            name='priority',
            field=models.PositiveSmallIntegerField(default=30),
        ),
        migrations.AlterField(
            model_name='goal',
            name='status',
            field=models.CharField(default='active', max_length=255, choices=[('active', 'Active'), ('archived', 'Archived'), ('abandoned', 'Abandoned')]),
        ),
        migrations.AlterField(
            model_name='goal',
            name='target_amount',
            field=models.PositiveSmallIntegerField(default=5),
        ),
        migrations.AlterField(
            model_name='goal',
            name='type',
            field=models.CharField(default='minutes', max_length=255),
        ),
    ]
