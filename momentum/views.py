from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.timezone import utc
from datetime import datetime
from django.conf import settings
import json

from .models import Goal, Entry

#@login_required
def dashboard(request):
    # Get all the user's goals
    goals = Goal.objects.filter(Q(owner=request.user),
                                      status='active').distinct().order_by('priority')

    return render_to_response('dashboard.html', {'goals': goals,
                                                 'request': request,
                                                 'key': settings.WEB_KEY})


def goal(request, goal_slug):
    # Get the goal
    goal = Goal.objects.get(slug=goal_slug, owner=request.user)

    return render_to_response('goal.html', {'goal': goal,
                                            'request': request,
                                            'key': settings.WEB_KEY})


def timer(request, goal_slug):
    # Get the goal
    goal = Goal.objects.get(slug=goal_slug)

    # Get the web key
    web_key = request.GET.get('key', '')
    if web_key != '' and web_key == settings.WEB_KEY:
        # Get the latest entry
        if len(goal.entries.all()) > 0:
            latest_entry = list(goal.entries.all())[-1]

            # If there's a stop time, create a new entry
            if latest_entry.stop_time:
                entry = Entry()
                entry.goal = goal
                entry.save()
            else:
                # No stop time, so add it
                latest_entry.stop_time = datetime.utcnow().replace(tzinfo=utc)
                latest_entry.amount = (latest_entry.stop_time - latest_entry.time).total_seconds()
                latest_entry.save()
        else:
            # Nothing yet, so create a new entry and start it
            entry = Entry()
            entry.goal = goal
            entry.save()

        return JsonResponse(json.dumps({'status': 'success'}), safe=False)
    else:
        return JsonResponse(json.dumps({'status': 'error'}), safe=False)
