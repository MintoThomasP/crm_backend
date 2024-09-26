
from app_project.models import CommentFile, Comments, Project, ProjectTask, ProjectTaskFile, ProjectTaskTiming, TaskReviews
from rest_framework import serializers


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
'SortId',
'ProjectId',
'CompanyId',
'ProjectName',
'Description',
'StartDate',
'EndDate',
'Duration',
'Status',
'ClientId',
'BusinessCategoryId',
'Address',
'ProjectScopeId',
'ProjectArea',
'EstimateAmount',
'SurveyDate',
'Assignedto',
'GoogleMapLink',
'ActiveStatus')
        

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
'TotalDuration',
'Status',
'CreatedDate',
'ScheduledDeadline',
'StartDate',
'EndDate',
'TaskPoint',
'TaskType',
'RefId',
'CompletionPoint',
'VerifiedBy',
'IsRepeated',
'RepeatInterval',
'ExtraAccess',
'NeedVerification',
'AccessTo',
'ClientId',
'ScheduledDays',
'NextScheduledDate',
'Interval',
'IsTemplate',
'CompanyId',
'MarkAsClientVisit',
'TempleteType'
        )


class ProjectTaskTimingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectTaskTiming
        fields = (
'SortId',
'ProjectTaskTimingId',
'ProjectTaskId',
'StartDate',
'EndDate',
'Duration',
'Note'
        )

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
                  'TaskFile'
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
        
class CommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comments
        fields = ('SortId',
                  'CommentId',
                  'ProjectTaskId',
                  'Comment',
                  'CommentedBy',
                  'Status')
        
class CommentFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentFile
        fields = ('SortId',
                  'CommentFileId',
                  'CommentId',
                  'CommentFile')
        

        
