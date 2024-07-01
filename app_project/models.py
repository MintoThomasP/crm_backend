from django.db import models
from datetime import datetime
import uuid

# Create your models here.


class Project(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectName = models.CharField(blank=True, null=True, max_length=300)
    Description=models.TextField(blank=True, null=True)
    StartDate=models.DateTimeField(default=datetime.now)
    EndDate=models.CharField(blank=True, null=True, max_length=100)
    Duration=models.IntegerField(default=0)
    Status=models.ForeignKey('app_default.TaskStatus',on_delete=models.CASCADE)
    ClientId=models.CharField(blank=True, null=True, max_length=50)

class ProjectTask(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectTaskId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectId=models.CharField(blank=True, null=True, max_length=50)
    TaskAssignedTo=models.CharField(blank=True, null=True, max_length=100)
    TaskAssignedBy=models.CharField(blank=True, null=True, max_length=100)
    Title=models.CharField(blank=True, null=True, max_length=300)
    Description=models.TextField(blank=True, null=True)
    Duration=models.CharField(blank=True, null=True, max_length=50)
    Status=models.CharField(blank=True, null=True, max_length=300)
    CreatedDate=models.CharField(blank=True, null=True, max_length=15)
    ScheduledDeadline=models.CharField(blank=True, null=True, max_length=100)
    StartDate=models.CharField(blank=True, null=True, max_length=100)
    EndDate=models.CharField(blank=True, null=True, max_length=100)
    TaskPoint=models.IntegerField(default=0)
    TaskType=models.CharField(blank=True, null=True, max_length=100)
    RefId=models.CharField(blank=True, null=True, max_length=50)
    CompletionPoint=models.IntegerField(default=0)
    VerifiedBy=models.CharField(blank=True, null=True, max_length=50)


class ProjectTaskFile(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectTaskFileId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectTaskId=models.CharField(blank=True, null=True, max_length=50)
    TaskFile=models.FileField(null=True,blank=True, upload_to='Taskfiles')



class TaskReviews(models.Model):
    SortId=models.DateTimeField(editable=False, default=datetime.now)
    TaskReviewId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(max_length=50, blank=True, null=True)
    TaskReview=models.TextField(blank=True, null=True)
    ProjectTaskId=models.CharField(blank=True, null=True, max_length=50)


class Comments(models.Model):
    SortId=models.DateTimeField(editable=False, default=datetime.now)
    CommentId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectTaskId=models.CharField(blank=True, null=True, max_length=50)
    Comment=models.TextField(blank=True, null=True)
    CommentedBy=models.CharField(blank=True, null=True, max_length=50)
    Status=models.IntegerField(default=0)

    

class CommentFile(models.Model):
    SortId=models.DateTimeField(editable=False, default=datetime.now)
    CommentFileId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CommentId=models.CharField(blank=True, null=True, max_length=50)
    CommentFile=models.FileField(null=True,blank=True, upload_to='Commentfiles')
