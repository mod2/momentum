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

from .models import Goal, Entry, Folder

@login_required
def dashboard(request):
    fullscreen = request.GET.get('fullscreen', False)

    # Get all the user's goals
    unfoldered_goals = [x for x in Goal.objects.filter(Q(owner=request.user),
                                                    status='active',
                                                    folder__isnull=True)
                                                .distinct()
                                                .order_by('priority') if not x.done_today()]

    # Now sort stale first
    unfoldered_goals = sorted(unfoldered_goals, key=lambda k: 1 - k.stale())

    active_folders = Folder.objects.filter(Q(owner=request.user)).distinct().order_by('order')

    # Get the latest entries
    latest_entries = Entry.objects.filter(goal__owner=request.user).order_by('-time')[:5]

    return render_to_response('dashboard.html', {'unfoldered_goals': unfoldered_goals,
                                                 'folders': active_folders,
                                                 'request': request,
                                                 'latest_entries': latest_entries,
                                                 'fullscreen': fullscreen,
                                                 'key': settings.WEB_KEY})

@login_required
def organize(request):
    # Get all the user's goals
    unfoldered_goals = [x for x in Goal.objects.filter(Q(owner=request.user),
                                                    status='active',
                                                    folder__isnull=True)
                                                .distinct()
                                                .order_by('priority')]

    active_folders = Folder.objects.filter(Q(owner=request.user)).distinct().order_by('order')

    # Get the latest entries
    latest_entries = Entry.objects.filter(goal__owner=request.user).order_by('-time')[:5]

    return render_to_response('organize.html', {'unfoldered_goals': unfoldered_goals,
                                                'folders': active_folders,
                                                'request': request,
                                                'latest_entries': latest_entries,
                                                'key': settings.WEB_KEY})

@login_required
def goal(request, goal_id):
    fullscreen = request.GET.get('fullscreen', False)

    # Get the goal
    goal = Goal.objects.get(id=goal_id, owner=request.user)

    return render_to_response('goal.html', {'goal': goal,
                                            'request': request,
                                            'fullscreen': fullscreen,
                                            'key': settings.WEB_KEY})

def timer(request, goal_id):
    # Get the goal
    goal = Goal.objects.get(id=goal_id)

    # Get the web key and redirect flag
    web_key = request.GET.get('key', '')
    redirect = request.GET.get('redirect', '')

    if web_key != '' and web_key == settings.WEB_KEY:
        current_amount = goal.get_current_amount_converted()

        # Get the latest entry
        if goal.entries.count() > 0:
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

def save(request, goal_id):
    # Get the goal
    goal = Goal.objects.get(id=goal_id)

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
    goals = Goal.objects.filter(status='active')

    # Get the web key and redirect flag
    web_key = request.GET.get('key', '')

    if web_key != '' and web_key == settings.WEB_KEY:
        for goal in goals:
            if goal.type in ['minutes', 'hours']:
                current_amount = goal.get_current_amount()
                current_elapsed = goal.get_current_elapsed_time()

                # Whether we're over the target amount
                over = (goal.get_current_amount_converted() >= goal.target_amount)

                goal_list.append({
                    'id': goal.id,
                    'slug': goal.slug,
                    'over': over,
                    'current_amount': goal.seconds_to_mm_ss(current_amount),
                    'current_elapsed': goal.seconds_to_mm_ss(current_elapsed),
                    'current_elapsed_in_seconds': '{0:.0f}'.format(current_elapsed),
                    'current_percentage': '{0:.2f}'.format(goal.get_current_percentage()),
                })

        return JsonResponse(json.dumps(goal_list), safe=False)
    else:
        return JsonResponse(json.dumps({'status': 'error'}), safe=False)

def update_goals(request):
    if request.is_ajax() and request.method == 'POST':
        order = json.loads(request.body.decode('utf-8'))['order']

        for i, goal_id in enumerate(order):
            goal = Goal.objects.get(id=goal_id)
            goal.priority = i
            goal.save()

        return JsonResponse(json.dumps({ "status": "success" }), safe=False)
