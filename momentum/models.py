from __future__ import unicode_literals, division

from django.db import models
from django.utils import timezone
from django.utils.timezone import utc
from django.contrib import auth
from datetime import datetime, timedelta, time

class Goal(models.Model):
    STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('abandoned', 'Abandoned'),
    )

    name = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, choices=STATUS)
    priority = models.PositiveSmallIntegerField(null=False, default=0)
    owner = models.ForeignKey(auth.models.User, related_name='goals', null=False)

    # Examples:
    # target_amount=15, type=minutes, period=day
    # target_amount=1, type=times, period=day
    # target_amount=10, type=times, period=year
    # target_amount=50000, type=words
    target_amount = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    type = models.CharField(max_length=255) # times/minutes/hours/words/pages/etc.
    period = models.CharField(max_length=255, blank=True, null=True) # day/week/month/year, optional

    # deadline

    def __unicode__(self):
        return self.name

    def in_progress(self):
        if len(self.entries.all()) > 0:
            last_entry = list(self.entries.all())[-1]
            if not last_entry.stop_time:
                return True
            else:
                return False
        else:
            return False

    def convert_to_resolution(self, duration):
        if self.type == "minutes":
            return (duration % 3600) / 60.0
        elif self.type == "hours":
            return duration / 3600.0
        else:
            return duration

    def get_current_elapsed_time(self):
        """ Returns current elapsed time in seconds. """

        if len(self.entries.all()) > 0:
            now = datetime.utcnow().replace(tzinfo=utc)
            last_entry = list(self.entries.all())[-1]

            # If we're stopped, there's no current elapsed time
            if last_entry.stop_time:
                return 0

            return (now - last_entry.time).total_seconds()

            # if self.type == "minutes":
            #     return (duration % 3600) / 60.0
            # elif self.type == "hours":
            #     return duration / 3600.0
            # else:
            #     return duration

        return 0

    def get_current_elapsed_time_converted(self):
        return self.convert_to_resolution(self.get_current_elapsed_time())

    def get_current_amount(self):
        # TODO: expand to week/month/year

        if self.period == "day":
            # Get all entries for this goal today and sum up the amounts

            #now = datetime.utcnow().replace(tzinfo=utc)
            now = datetime.now()
            today = now.date()
            tomorrow = today + timedelta(1)
            today_start = datetime.combine(today, time())
            today_end = datetime.combine(tomorrow, time())

            #entries = Entry.objects.filter(goal=self, time__lte=today_end, time__gte=today_start)
            entries = self.entries.filter(time__lte=today_end, time__gte=today_start)

            total_time = 0
            for entry in entries:
                if entry.amount:
                    total_time += entry.amount
                else:
                    # No stop time yet, so use now, converting to the resolution
                    total_time += self.get_current_elapsed_time()

            return total_time

        return 0

    def get_current_amount_converted(self):
        return self.convert_to_resolution(self.get_current_amount())

    def get_current_percentage(self):
        return min((self.get_current_amount_converted() / self.target_amount) * 100.0, 100.0)

    def get_amount_for_day(self, day):
        # Get all entries for this goal on this day and sum up the amounts

        tomorrow = day + timedelta(1)
        today_start = datetime.combine(day, time())
        today_end = datetime.combine(tomorrow, time())

        entries = self.entries.filter(time__lte=today_end, time__gte=today_start)

        total_time = 0
        for entry in entries:
            if entry.amount:
                total_time += entry.amount
            else:
                # No stop time yet, so use now, converting to the resolution
                #total_time += self.get_current_elapsed_time()
                pass

        return total_time

    def get_amount_for_day_converted(self, day):
        return self.convert_to_resolution(self.get_amount_for_day(day))

    def get_percentage_for_day(self, day):
        return min((self.get_amount_for_day_converted(day) / self.target_amount) * 100.0, 100.0)

    def get_days(self):
        # Returns list of days that have entries
        days = set([x.time.date() for x in self.entries.all().order_by('-time')])
        return days

    def get_entries_by_day(self):
        # Returns list of days with entries for each
        days = self.get_days()

        day_list = []

        for day in days:
            next_day = day + timedelta(1)
            this_day_start = datetime.combine(day, time())
            this_day_end = datetime.combine(next_day, time())

            entries = self.entries.filter(time__lte=this_day_end, time__gte=this_day_start)

            day_list.append({
                'date': day,
                'entries': entries,
                'amount': self.get_amount_for_day_converted(day),
                'percentage': self.get_percentage_for_day(day),
            })

        print day_list
        return day_list

class Entry(models.Model):
    goal = models.ForeignKey(Goal, related_name='entries')
    amount = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    time = models.DateTimeField(auto_now_add=True)
    stop_time = models.DateTimeField(null=True, default=None, blank=True)

    def __unicode__(self):
        return "Entry"

    def convert_to_resolution(self, duration):
        if self.goal.type == "minutes":
            return (duration % 3600) / 60.0
        elif self.goal.type == "hours":
            return duration / 3600.0
        else:
            return duration

    def get_elapsed_time(self):
        # If there's already a stop time then we're good
        if self.stop_time:
            return self.amount

        now = datetime.utcnow().replace(tzinfo=utc)
        return (now - self.time).total_seconds()

    def get_elapsed_time_converted(self):
        return self.convert_to_resolution(self.get_elapsed_time())

    class Meta:
        verbose_name_plural = "entries"
