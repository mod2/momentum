from __future__ import unicode_literals, division

from django.db import models
from django.utils import timezone
from django.utils.timezone import utc
from django.contrib import auth
from datetime import datetime, timedelta, time
import pytz

from autoslug import AutoSlugField

class Goal(models.Model):
    STATUS = (
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('abandoned', 'Abandoned'),
    )

    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name')
    status = models.CharField(max_length=255, choices=STATUS)
    priority = models.PositiveSmallIntegerField(null=False, default=0)
    owner = models.ForeignKey(auth.models.User, related_name='goals', null=False)

    # Examples:
    # target_amount=15, type=minutes, period=day
    # target_amount=1, type=times, period=day
    # target_amount=10, type=times, period=year
    # target_amount=50000, type=words
    target_amount = models.PositiveSmallIntegerField(default=0)
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
            return (duration / 3600.0) * 60.0
        elif self.type == "hours":
            return duration / 3600.0
        else:
            return duration

    def get_current_elapsed_time(self):
        """ Returns current elapsed time in seconds. """

        if len(self.entries.all()) > 0:
            now = timezone.now()
            last_entry = list(self.entries.all())[-1]

            # If we're stopped, there's no current elapsed time
            if last_entry.stop_time:
                return 0

            return (now - last_entry.time).total_seconds()

        return 0

    def get_current_elapsed_time_converted(self):
        return self.convert_to_resolution(self.get_current_elapsed_time())

    def get_current_amount(self):
        # TODO: expand to week/month/year

        if self.period == "day":
            # Get all entries for this goal today and sum up the amounts

            now = timezone.localtime(timezone.now(), timezone.get_current_timezone())
            today = now.date()
            tomorrow = today + timedelta(1)
            today_start = datetime.combine(today, time())
            today_end = datetime.combine(tomorrow, time())

            # Convert back to UTC
            tz = timezone.get_current_timezone()
            d_tz = tz.normalize(tz.localize(today_start))
            today_start_utc = d_tz.astimezone(utc)
            d_tz = tz.normalize(tz.localize(today_end))
            today_end_utc = d_tz.astimezone(utc)

            entries = self.entries.filter(time__lte=today_end_utc, time__gte=today_start_utc)

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

        # Convert back to UTC
        tz = timezone.get_current_timezone()
        d_tz = tz.normalize(tz.localize(today_start))
        today_start_utc = d_tz.astimezone(utc)
        d_tz = tz.normalize(tz.localize(today_end))
        today_end_utc = d_tz.astimezone(utc)

        entries = self.entries.filter(time__lte=today_end_utc, time__gte=today_start_utc)

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

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_days(self):
        """ Returns list of days that have entries """

        entries = self.entries.all().order_by('time')

        start_date = timezone.localtime(entries[0].time, timezone.get_current_timezone()).date()
        end_date = timezone.now().date()

        return [x for x in self.daterange(start_date, end_date)]

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

        return day_list


class Entry(models.Model):
    goal = models.ForeignKey(Goal, related_name='entries')
    amount = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    time = models.DateTimeField()
    stop_time = models.DateTimeField(null=True, default=None, blank=True)

    def save(self, *args, **kwargs):
        if not self.time:
            self.time = timezone.now()

        if self.stop_time:
            self.amount = (self.stop_time - self.time).total_seconds()

        return super(Entry, self).save(*args, **kwargs)

    def __unicode__(self):
        return "Entry"

    def convert_to_resolution(self, duration):
        if self.goal.type == "minutes":
            return (duration / 3600.0) * 60.0
        elif self.goal.type == "hours":
            return duration / 3600.0
        else:
            return duration

    def get_elapsed_time(self):
        # If there's already a stop time then we're good
        if self.stop_time:
            return self.amount

        now = timezone.now()
        return (now - self.time).total_seconds()

    def get_elapsed_time_converted(self):
        return self.convert_to_resolution(self.get_elapsed_time())

    class Meta:
        verbose_name_plural = "entries"
