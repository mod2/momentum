from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.timezone import utc
from datetime import datetime
from django.conf import settings
import json

from .models import Goal, Entry

@login_required
def dashboard(request):
    # Get all the user's goals
    goals = Goal.objects.filter(Q(owner=request.user),
                                      status='active').distinct().order_by('priority')

    latest_entries = Entry.objects.filter(goal__owner=request.user).order_by('-time')[:5]

    return render_to_response('dashboard.html', {'goals': goals,
                                                 'request': request,
                                                 'latest_entries': latest_entries,
                                                 'key': settings.WEB_KEY})

@login_required
def goal(request, goal_slug):
    # Get the goal
    goal = Goal.objects.get(slug=goal_slug, owner=request.user)

    return render_to_response('goal.html', {'goal': goal,
                                            'request': request,
                                            'key': settings.WEB_KEY})


def timer(request, goal_slug):
    # Get the goal
    goal = Goal.objects.get(slug=goal_slug)

    # Get the web key and redirect flag
    web_key = request.GET.get('key', '')
    redirect = request.GET.get('redirect', '')

    if web_key != '' and web_key == settings.WEB_KEY:
        current_amount = goal.get_current_amount_converted()

        # Get the latest entry
        if len(goal.entries.all()) > 0:
            latest_entry = list(goal.entries.all())[-1]

            # If there's a stop time, create a new entry
            if latest_entry.stop_time:
                entry = Entry()
                entry.goal = goal
                entry.target_amount = goal.target_amount
                entry.save()
            else:
                # No stop time, so add it
                latest_entry.stop_time = datetime.utcnow().replace(tzinfo=utc)
                latest_entry.amount = (latest_entry.stop_time - latest_entry.time).total_seconds()
                latest_entry.save()
                current_amount = goal.get_current_amount_converted()
        else:
            # Nothing yet, so create a new entry and start it
            entry = Entry()
            entry.goal = goal
            entry.target_amount = goal.target_amount
            entry.save()

        if redirect == 'true':
            # TODO: update this to use django.shortcuts.redirect
            # (I tried, but it wasn't working)
            return HttpResponseRedirect('/')
        else:
            return JsonResponse(json.dumps({'status': 'success', 'amount': round(current_amount, 1) }), safe=False)
    else:
        return JsonResponse(json.dumps({'status': 'error'}), safe=False)

def save(request, goal_slug):
    # Get the goal
    goal = Goal.objects.get(slug=goal_slug)

    # Get the web key and redirect flag
    web_key = request.GET.get('key', '')
    amount = request.GET.get('amount', '')
    redirect = request.GET.get('redirect', '')

    if web_key != '' and web_key == settings.WEB_KEY:
        # Nothing yet, so create a new entry and start it
        entry = Entry()
        entry.goal = goal
        entry.amount = amount
        entry.target_amount = goal.target_amount
        entry.save()

        if redirect == 'true':
            # TODO: update this to use django.shortcuts.redirect
            # (I tried, but it wasn't working)
            return HttpResponseRedirect('/')
        else:
            return JsonResponse(json.dumps({'status': 'success',
                                            'amount': amount,
                                            'total_amount': goal.get_current_amount(),
                                            'percentage': goal.get_current_percentage()
                                            }), safe=False)
    else:
        return JsonResponse(json.dumps({'status': 'error'}), safe=False)

def status(request):
    # Get all goals and return the current/elapsed times for each
    goal_list = []
    goals = Goal.objects.all()

    # Get the web key and redirect flag
    web_key = request.GET.get('key', '')

    if web_key != '' and web_key == settings.WEB_KEY:
        for goal in goals:
            goal_list.append({
                'slug': goal.slug,
                'current_amount': '{0:.1f}'.format(goal.get_current_amount_converted()),
                'current_elapsed': '{0:.1f}'.format(goal.get_current_elapsed_time_converted()),
                'current_elapsed_in_seconds': '{0:.0f}'.format(goal.get_current_elapsed_time()),
                'current_percentage': '{0:.1f}'.format(goal.get_current_percentage()),
            })

        return JsonResponse(json.dumps(goal_list), safe=False)
    else:
        return JsonResponse(json.dumps({'status': 'error'}), safe=False)

def update_goals(request):
    if request.is_ajax() and request.method == 'POST':
        order = json.loads(request.body)['order']

        goals = Goal.objects.filter(slug__in=order.keys())
        for goal in goals:
            goal.priority = order[unicode(goal.slug)]
            goal.save()

        return JsonResponse(json.dumps({ "status": "success" }), safe=False)
