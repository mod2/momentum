from django.contrib import admin

from .models import Goal, Entry

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'target_amount', 'type', 'period', 'priority', 'status')


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('goal', 'amount', 'target_amount', 'time', 'stop_time')
