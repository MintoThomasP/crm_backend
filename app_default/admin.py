from django.contrib import admin

from app_default.models import TaskStatus

# Register your models here.


class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ('StatusId',
'Status',
'Point',)
admin.site.register(TaskStatus, TaskStatusAdmin)