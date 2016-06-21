from django.core.management.base import BaseCommand, CommandError

from momentum.models import Goal, Entry
from django.contrib.auth.models import User

import sqlite3
import datetime

class Command(BaseCommand):
    args = ''
    help = 'Updates statuses to be just active/inactive'

    def handle(self, *args, **options):
        try:
            goals = Goal.objects.all()
            for goal in goals:
                if goal.status != 'active':
                    goal.status = 'inactive'
                    goal.save()
        except Exception as e:
            print(e)
