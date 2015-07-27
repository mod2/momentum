# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import autoslug.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('momentum', '0012_goal_stale_period'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', autoslug.fields.AutoSlugField(editable=False)),
                ('order', models.PositiveSmallIntegerField(default=100)),
                ('owner', models.ForeignKey(related_name='folders', default=1, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['order'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='goal',
            name='folder',
            field=models.ForeignKey(related_name='goals', blank=True, to='momentum.Folder', null=True),
            preserve_default=True,
        ),
    ]
