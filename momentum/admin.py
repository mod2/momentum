from django.contrib import admin

from .models import Goal, Entry, Folder, Context

@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ('name', 'context', 'target_amount', 'type', 'period', 'priority', 'status', 'last_entry_date', 'last_completed_date',)


@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ('goal', 'amount', 'target_amount', 'time', 'stop_time',)


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'context',)


@admin.register(Context)
class ContextAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color',)
