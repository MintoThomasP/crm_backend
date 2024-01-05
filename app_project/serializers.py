from app_project.models import Project, ProjectTask, TaskReviews
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
'SortId',
'ProjectId',
'ProjectName',
'Description',
'StartDate',
'Duration',
'Status',
'ClientId')
        

class ProjectTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTask
        fields = (
'SortId',
'ProjectTaskId',
'ProjectId',
'TaskAssignedTo',
'TaskAssignedBy',
'Title',
'Description',
'Duration',
'Status',
'CreatedDate',
'StartDate',
'EndDate',
'TaskPoint',
'CompletionPoint')
        

class TaskReviewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskReviews
        fields = (
'SortId',
'TaskReviewId',
'ClientId',
'TaskReview',
'ProjectTaskId'
)