from __future__ import unicode_literals

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils.timezone import utc
from django.views.decorators.cache import never_cache
from datetime import datetime
from django.conf import settings
import json

from .models import Goal, Entry, Folder, Context

@login_required
def dashboard(request):
    # Redirect to first context
    ctx = Context.objects.first()
    return redirect('context', context_slug=ctx.slug)

@login_required
def context_detail(request, context_slug):
    fullscreen = request.GET.get('fullscreen', False)

    # Get the context
    ctx = Context.objects.get(slug=context_slug)

    # Get all the user's goals
    unfoldered_goals = [x for x in Goal.objects.filter(Q(owner=request.user),
                                                    status='active',
                                                    context__slug=context_slug,
                                                    folder__isnull=True)
                                                .distinct()
                                                .order_by('priority') if not x.done_today()]

    # Now sort stale first
    unfoldered_goals = sorted(unfoldered_goals, key=lambda k: 1 - k.stale())

    active_folders = Folder.objects.filter(Q(owner=request.user, context__slug=context_slug)).distinct().order_by('order')

    # Get the latest entries
    latest_entries = Entry.objects.filter(goal__owner=request.user, goal__context__slug=context_slug).select_related('goal').order_by('-time')[:5]

    return render_to_response('context.html', {'unfoldered_goals': unfoldered_goals,
                                               'ctx': ctx,
                                                'folders': active_folders,
                                                'request': request,
                                                'latest_entries': latest_entries,
                                                'fullscreen': fullscreen,
                                                'key': settings.WEB_KEY})

@login_required
def organize(request, context_slug):
    # Get the context
    ctx = Context.objects.get(slug=context_slug)

    # Get all the user's goals
    unfoldered_goals = [x for x in Goal.objects.filter(Q(owner=request.user),
                                                    context__slug=context_slug,
                                                    status='active',
                                                    folder__isnull=True)
                                                .distinct()
                                                .order_by('priority')]

    active_folders = Folder.objects.filter(Q(owner=request.user, context__slug=context_slug)).distinct().order_by('order')

    # Get the latest entries
    latest_entries = Entry.objects.filter(goal__owner=request.user).order_by('-time')[:5]

    return render_to_response('organize.html', {'unfoldered_goals': unfoldered_goals,
                                                'ctx': ctx,
                                                'folders': active_folders,
                                                'request': request,
                                                'latest_entries': latest_entries,
                                                'key': settings.WEB_KEY})

@login_required
def goal(request, context_slug, goal_id):
    # Get the context
    ctx = Context.objects.get(slug=context_slug)

    fullscreen = request.GET.get('fullscreen', False)

    # Get the goal
    goal = Goal.objects.get(id=goal_id, owner=request.user, context__slug=context_slug)

    return render_to_response('goal.html', {'goal': goal,
                                            'ctx': ctx,
                                            'request': request,
                                            'fullscreen': fullscreen,
                                            'key': settings.WEB_KEY})


# API calls

@never_cache
def timer(request, context_slug, goal_id):
    print("Here")

    # Get the goal
    goal = Goal.objects.get(context__slug=context_slug, id=goal_id)

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

@never_cache
def save(request, context_slug, goal_id):
    # Get the goal
    goal = Goal.objects.get(context__slug=context_slug, id=goal_id)

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

@never_cache
def status(request, context_slug):
    # Get all goals and return the current/elapsed times for each

    import time
    goal_list = []
    goals = Goal.objects.filter(status='active', context__slug=context_slug)

    # Get the web key and redirect flag
    web_key = request.GET.get('key', '')

    if web_key != '' and web_key == settings.WEB_KEY:
        for goal in goals:
            if goal.type in ['minutes', 'hours']:
                metadata = goal.get_current_metadata()

                goal_list.append({
                    'id': goal.id,
                    'over': metadata['over'],
                    'current_amount': metadata['current_amount_mm_ss'],
                    'current_elapsed': metadata['current_elapsed_mm_ss'],
                    'current_elapsed_in_seconds': '{0:.0f}'.format(metadata['current_elapsed']),
                    'current_percentage': '{0:.2f}'.format(metadata['current_percentage']),
                })

        return JsonResponse({'goals': goal_list})
    else:
        return JsonResponse({'status': 'error'})

@never_cache
def update_goals(request, context_slug):
    if request.is_ajax() and request.method == 'POST':
        order = json.loads(request.body.decode('utf-8'))['order']

        for i, goal_id in enumerate(order):
            goal = Goal.objects.get(id=goal_id, context__slug=context_slug)
            goal.priority = i
            goal.save()

        return JsonResponse(json.dumps({ "status": "success" }), safe=False)
