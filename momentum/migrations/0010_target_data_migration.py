# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def populate_target_amount(apps, schema_editor):
    Entry = apps.get_model("momentum", "Entry")

    for entry in Entry.objects.all():
        entry.target_amount = entry.goal.target_amount
        entry.save()

class Migration(migrations.Migration):

    dependencies = [
        ('momentum', '0009_entry_target_amount'),
    ]

    operations = [
        migrations.RunPython(populate_target_amount),
    ]
