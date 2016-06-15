from __future__ import unicode_literals, division

from django.db import models
from django.utils import timezone
from django.utils.timezone import utc
from django.contrib import auth
from datetime import datetime, timedelta, time
import colorsys
import math
import pytz

from autoslug import AutoSlugField

class Context(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name')
    owner = models.ForeignKey(auth.models.User, related_name='contexts', null=False, default=1)
    color = models.IntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.name

    def as_hex(self, rgb):
        """ Returns representation of color in hex. """
        r = int(math.ceil(rgb[0] * 255))
        g = int(math.ceil(rgb[1] * 255))
        b = int(math.ceil(rgb[2] * 255))

        return "#{:02x}{:02x}{:02x}".format(r, g, b)

    def header_bg(self):
        return self.as_hex(colorsys.hsv_to_rgb(self.color / 360, .46, .45))

    def footer_bg(self):
        return self.as_hex(colorsys.hsv_to_rgb(self.color / 360, .36, .25))

    def header_text(self):
        return self.as_hex(colorsys.hsv_to_rgb(self.color / 360, .26, .98))

    def footer_text(self):
        return self.as_hex(colorsys.hsv_to_rgb(self.color / 360, .26, .98))

    def footer_head(self):
        return self.as_hex(colorsys.hsv_to_rgb(self.color / 360, .46, .65))


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
    context = models.ForeignKey('Context', null=True, blank=True, related_name='goals')
    folder = models.ForeignKey('Folder', null=True, blank=True, related_name='goals')

    # Examples:
    # target_amount=15, type=minutes, period=day
    # target_amount=1, type=times, period=day
    # target_amount=10, type=times, period=year
    # target_amount=50000, type=words
    target_amount = models.PositiveSmallIntegerField(default=1)
    type = models.CharField(max_length=255, default='minutes') # times/minutes/hours/words/pages/etc.
    period = models.CharField(max_length=255, blank=True, null=True, default='day') # day/week/month/year, optional

    stale_period = models.PositiveSmallIntegerField(default=0)

    visibility_period = models.PositiveSmallIntegerField(default=0)
    last_entry_date = models.DateField(null=True, blank=True, default=timezone.now())
    last_completed_date = models.DateField(null=True, blank=True, default=timezone.now())

    def __str__(self):
        response = '{}/{}'.format(self.context.slug, self.name)
        if self.folder:
            response += ' ({})'.format(self.folder.slug)

        return response

    def in_progress(self):
        if self.type in ['words', 'times']:
            return False

        if self.entries.count() > 0:
            last_entry = self.entries.last()
            if not last_entry.stop_time:
                return True
            else:
                return False
        else:
            return False
    
    def done_today(self):
        if self.get_current_amount_converted() >= self.target_amount and not self.in_progress():
            return True

        if self.visibility_period > 0 and (timezone.now().date() - self.last_completed_date).days < self.visibility_period:
            return True
        
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

        if self.entries.count() > 0:
            now = timezone.now()
            last_entry = self.entries.last()

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

    def get_current_amount_converted(self, amt=None):
        if amt is not None:
            return self.convert_to_resolution(amt)
        else:
            return self.convert_to_resolution(self.get_current_amount())

    def get_current_amount_mm_ss(self):
        return self.seconds_to_mm_ss(self.get_current_amount())

    def get_current_elapsed_time_mm_ss(self):
        return self.seconds_to_mm_ss(self.get_current_elapsed_time())

    def get_current_percentage(self, amt=None):
        if amt is not None:
            return min((amt / self.target_amount) * 100.0, 100.0)
        else:
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

    def seconds_to_mm_ss(self, seconds):
        m, s = divmod(seconds, 60)
        return '{:d}:{:02d}'.format(int(m), int(s))

    def get_percentage_for_day(self, day, target_amount=None):
        if not target_amount:
            target_amount = self.target_amount

        return min((self.get_amount_for_day_converted(day) / target_amount) * 100.0, 100.0)

    def get_current_metadata(self):
        current_amount = self.get_current_amount()
        current_amount_converted = self.get_current_amount_converted(current_amount)
        current_amount_mm_ss = self.seconds_to_mm_ss(current_amount)
        current_elapsed = self.get_current_elapsed_time()
        current_elapsed_mm_ss = self.seconds_to_mm_ss(current_elapsed)
        current_percentage = self.get_current_percentage(current_amount_converted)
        over = (current_amount_converted >= self.target_amount)

        response = {
            'current_amount': current_amount,
            'current_amount_converted': current_amount_converted,
            'current_amount_mm_ss': current_amount_mm_ss,
            'current_elapsed': current_elapsed,
            'current_elapsed_mm_ss': current_elapsed_mm_ss,
            'current_percentage': current_percentage,
            'over': over,
        }

        return response

    def daterange(self, start_date, end_date):
        for n in range(int ((end_date - start_date).days)):
            yield start_date + timedelta(n)

    def get_days(self):
        """ Returns list of days that have entries """

        entries = self.entries.all().order_by('time')

        if entries.count() > 0:
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

            amount = self.get_amount_for_day_converted(day)

            if self.type in ['minutes', 'hours']:
                display_amount = self.seconds_to_mm_ss(self.get_amount_for_day(day))
            else:
                display_amount = amount

            over = (amount >= target_amount)

            day_list.append({
                'date': day,
                'entries': entries,
                'over': over,
                'target_amount': target_amount,
                'amount': amount,
                'display_amount': display_amount,
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

    def get_display_type(self):
        if self.type == 'minutes' and self.target_amount == 1:
            return 'minute'

        if self.type == 'words' and self.target_amount == 1:
            return 'word'

        return self.type

    def stale(self):
        """ Check to see if this goal is stale. """

        stale_period = self.get_stale_period()

        # Take the visibility period into account if it's there
        if self.visibility_period > 0:
            stale_period += self.visibility_period

        if self.status == 'active' and stale_period != 0 and self.days_since_last_entry() > stale_period:
            return True

        return False

    def width(self):
        if self.type == 'minutes':
            # Scale to the number of minutes, 10+ is full width
            return min(self.target_amount * 16, 160)

        return 160

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
    context = models.ForeignKey('Context', null=True, blank=True, related_name='folders')

    def __str__(self):
        return '{}/{}'.format(self.context.slug, self.slug)

    def active_goals(self):
        goals = self.goals.filter(status='active').distinct().order_by('priority')

        # Now sort stale first
        goals = sorted(goals, key=lambda k: 1 - k.stale())

        return goals

    def active_goals_today(self):
        foo = [x for x in self.goals.filter(status='active').distinct().order_by('priority')]
        goals = [x for x in self.goals.filter(status='active').distinct().order_by('priority') if not x.done_today()]

        # Now sort stale first
        goals = sorted(goals, key=lambda k: 1 - k.stale())

        return goals


    class Meta:
        ordering = ['order']
