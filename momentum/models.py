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
    status = models.CharField(max_length=255, choices=STATUS, default='active')
    priority = models.PositiveSmallIntegerField(null=False, default=30)
    owner = models.ForeignKey(auth.models.User, related_name='goals', null=False, default=1)

    folder = models.ForeignKey('Folder', null=True, blank=True, related_name='goals')

    # Examples:
    # target_amount=15, type=minutes, period=day
    # target_amount=1, type=times, period=day
    # target_amount=10, type=times, period=year
    # target_amount=50000, type=words
    target_amount = models.PositiveSmallIntegerField(default=5)
    type = models.CharField(max_length=255, default='minutes') # times/minutes/hours/words/pages/etc.
    period = models.CharField(max_length=255, blank=True, null=True, default='day') # day/week/month/year, optional

    # deadline

    stale_period = models.PositiveSmallIntegerField(default=0)

    def __unicode__(self):
        return self.name

    def in_progress(self):
        if self.type in ['words', 'times']:
            return False

        if len(self.entries.all()) > 0:
            last_entry = list(self.entries.all())[-1]
            if not last_entry.stop_time:
                return True
            else:
                return False
        else:
            return False
    
    def done_today(self):
        return (self.get_current_amount_converted() >= self.target_amount)

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

    def get_percentage_for_day(self, day, target_amount=None):
        if not target_amount:
            target_amount = self.target_amount

        return min((self.get_amount_for_day_converted(day) / target_amount) * 100.0, 100.0)

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_days(self):
        """ Returns list of days that have entries """

        entries = self.entries.all().order_by('time')

        if len(entries) > 0:
            start_date = timezone.localtime(entries[0].time, timezone.get_current_timezone()).date()
            end_date = timezone.now().date()

            return [x for x in self.daterange(start_date, end_date)]
        else:
            return []

    def get_entries_by_day(self):
        # Returns list of days with entries for each
        days = self.get_days()
        days.reverse()

        day_list = []

        for day in days:
            next_day = day + timedelta(1)
            this_day_start = datetime.combine(day, time())
            this_day_end = datetime.combine(next_day, time())

            entries = self.entries.filter(time__lte=this_day_end, time__gte=this_day_start)

            if entries:
                target_amount = entries[0].target_amount
            else:
                target_amount = self.target_amount

            day_list.append({
                'date': day,
                'entries': entries,
                'target_amount': target_amount,
                'amount': self.get_amount_for_day_converted(day),
                'percentage': self.get_percentage_for_day(day, target_amount),
            })

        return day_list

    def days_since_last_entry(self):
        last_entry = self.entries.last()

        if last_entry:
            last_entry = last_entry.time.replace(tzinfo=utc).replace(hour=0, minute=0, second=0, microsecond=0)
            today = datetime.utcnow().replace(tzinfo=utc).replace(hour=0, minute=0, second=0, microsecond=0)
            days = (today - last_entry).days
        else:
            # Very far in the past, so it always shows up stale
            days = 100000

        return days

    def get_stale_period(self):
        from django.conf import settings

        # If the reading has a stale period, use it instead of the system default
        if self.stale_period > 0:
            stale_period = self.stale_period
        else:
            stale_period = settings.STALE_PERIOD

        return stale_period

    def stale(self):
        """ Check to see if this goal is stale. """

        stale_period = self.get_stale_period()

        if self.status == 'active' and stale_period != 0 and self.days_since_last_entry() > stale_period:
            return True

        return False

    def type_truncated(self):
        if self.type == 'minutes':
            return 'min'
        return self.type


class Entry(models.Model):
    goal = models.ForeignKey(Goal, related_name='entries')
    amount = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    target_amount = models.PositiveSmallIntegerField(null=True, default=0, blank=True)
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


class Folder(models.Model):
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from='name')
    order = models.PositiveSmallIntegerField(default=100)
    owner = models.ForeignKey(auth.models.User, related_name='folders', default=1)

    def __str__(self):
        return self.name

    def active_goals(self):
        return [x for x in self.goals.filter(status='active')
                                    .distinct()
                                    .order_by('priority') if not x.done_today()]

    class Meta:
        ordering = ['order']
