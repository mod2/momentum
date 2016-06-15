# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-15 13:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0016_auto_20160613_1150'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='last_completed_date',
            field=models.DateField(blank=True, default=datetime.datetime(2016, 6, 15, 13, 10, 55, 147615, tzinfo=utc), null=True),
        ),
        migrations.AddField(
            model_name='goal',
            name='last_entry_date',
            field=models.DateField(blank=True, default=datetime.datetime(2016, 6, 15, 13, 10, 55, 147662, tzinfo=utc), null=True),
        ),
        migrations.AddField(
            model_name='goal',
            name='visibility_period',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='context',
            name='color',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]