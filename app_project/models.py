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
    Duration=models.IntegerField(default=0)
    Status=models.CharField(blank=True, null=True, max_length=300)
    CreatedDate=models.DateTimeField(editable=False, default=datetime.now)
    StartDate=models.CharField(blank=True, null=True, max_length=100)
    EndDate=models.CharField(blank=True, null=True, max_length=100)
    TaskPoint=models.IntegerField(default=0)
    CompletionPoint=models.IntegerField(default=0)


class TaskReviews(models.Model):
    SortId=models.DateTimeField(editable=False, default=datetime.now)
    TaskReviewId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(max_length=50, blank=True, null=True)
    TaskReview=models.TextField(blank=True, null=True)
    ProjectTaskId=models.CharField(blank=True, null=True, max_length=50)
    
