from app_project.models import Project, ProjectTask, ProjectTaskFile, TaskReviews
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
'CompletionPoint',
'VerifiedBy')


class ProjectTaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTaskFile
        fields = ( 'SortId',
                  'ProjectTaskFileId',
                  'ProjectTaskId',
                  'TaskFile')
class SaveProjectTaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTaskFile
        fields = ( 'SortId',
                  'ProjectTaskFileId',
                  'ProjectTaskId',
                  )
        
class UploadProjectTaskFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTaskFile
        fields = (
                  'ProjectTaskFileId',
                  'TaskFile')

        

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