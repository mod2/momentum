from django.core.management.base import BaseCommand, CommandError

from momentum.models import Goal, Entry
from django.contrib.auth.models import User

import sqlite3
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Updates last_entry_date and last_completed_date to be accurate'

    def handle(self, *args, **options):
        try:
            goals = Goal.objects.all()
            for goal in goals:
                if goal.entries.last():
                    goal.last_entry_date = goal.entries.last().time.date()
                    # Technically this isn't accurate, but it should be good enough
                    goal.last_completed_date = goal.entries.last().time.date()
                    goal.save()
        except Exception as e:
            print(e)
