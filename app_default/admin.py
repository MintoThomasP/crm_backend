from django.contrib import admin

from app_default.models import TaskStatus, UserType

# Register your models here.


class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ('StatusId',
'Status',
'Point',)
admin.site.register(TaskStatus, TaskStatusAdmin)


class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('UserTypeId',
'UserType')
admin.site.register(UserType, UserTypeAdmin)