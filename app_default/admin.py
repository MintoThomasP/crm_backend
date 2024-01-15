from django.contrib import admin

from app_default.models import Designation, TaskStatus, UserGroup, UserType

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

class DesignationAdmin(admin.ModelAdmin):
    list_display = ('SortId',
                  'DesignationId',
                  'Designation',
                  )
admin.site.register(Designation, DesignationAdmin)


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('SortId',
                  'UserGroupId',
                  'UserGroup',
                  'AccessTo')
admin.site.register(UserGroup, UserGroupAdmin)


