# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('amount', models.PositiveSmallIntegerField(default=None, null=True, blank=True)),
                ('time', models.DateTimeField(auto_now_add=True)),
                ('stop_time', models.DateTimeField(default=None, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Goal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('status', models.CharField(max_length=255, choices=[('active', 'Active'), ('archived', 'Archived'), ('abandoned', 'Abandoned')])),
                ('target_amount', models.PositiveSmallIntegerField(default=None, null=True, blank=True)),
                ('type', models.CharField(max_length=255)),
                ('period', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entry',
            name='goal',
            field=models.ForeignKey(related_name='entries', to='momentum.Goal'),
            preserve_default=True,
        ),
    ]
