from django.contrib import admin

from app_project.models import Project

# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('SortId',
'ProjectId',
'ProjectName',
'Description',
'StartDate',
'Duration',
'Status')
admin.site.register(Project, ProjectAdmin)