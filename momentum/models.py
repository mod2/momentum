from __future__ import unicode_literals, division

from django.db import models
from model_utils.models import StatusModel

class Goal(StatusModel):
    STATUS = Choices(
        ('active', 'Active'),
        ('archived', 'Archived'),
        ('abandoned', 'Abandoned'),
    )

    name = models.CharField(max_length=255)

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


class Entry(models.Model):
    name = models.CharField(max_length=255)
    goal = models.ForeignKey(Goal, related_name='entries')

    amount = models.PositiveSmallIntegerField(null=True, default=None, blank=True)
    time = models.DateTimeField(auto_now=True, default=timezone.now())
    stop_time = models.DateTimeField(null=True, default=None, blank=True)

    def __unicode__(self):
        return self.name
