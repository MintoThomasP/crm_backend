from django.db import models
from datetime import datetime
import uuid
import pytz
from django.utils import timezone
# Create your models here.
from django.db.models.signals import post_save
from django.dispatch import receiver
from firebase_admin import messaging

class Project(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
    ProjectName = models.CharField(blank=True, null=True, max_length=300)
    Description=models.TextField(blank=True, null=True)
    StartDate=models.CharField(blank=True, null=True, max_length=50)
    EndDate=models.CharField(blank=True, null=True, max_length=100)
    Duration=models.IntegerField(default=0)
    Status=models.ForeignKey('app_default.TaskStatus',on_delete=models.CASCADE)
    ClientId=models.CharField(blank=True, null=True, max_length=50)
    BusinessCategoryId=models.CharField(blank=True, null=True, max_length=50)
    Address=models.TextField(blank=True, null=True)
    ProjectScopeId=models.CharField(blank=True, null=True, max_length=50)
    ProjectArea=models.CharField(blank=True, null=True, max_length=50)
    EstimateAmount=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    SurveyDate=models.CharField(blank=True, null=True, max_length=50)
    Assignedto=models.TextField(blank=True, null=True)
    GoogleMapLink=models.TextField(blank=True, null=True)
    ActiveStatus=models.BooleanField(default=True)
    # def save(self, *args, **kwargs):
    #     if not self.StartDate:
    #         # Convert current time to IST
    #         ist = pytz.timezone('Asia/Kolkata')
    #         self.StartDate = datetime.now(ist)
    #     super(Project, self).save(*args, **kwargs)

class ProjectTask(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectTaskId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectId=models.CharField(blank=True, null=True, max_length=50)
    TaskAssignedTo=models.CharField(blank=True, null=True, max_length=100)
    TaskAssignedBy=models.CharField(blank=True, null=True, max_length=100)
    Title=models.CharField(blank=True, null=True, max_length=300)
    Description=models.TextField(blank=True, null=True)
    Duration=models.CharField(default='0:10',max_length=50)
    TotalDuration=models.CharField(blank=True, null=True, max_length=50)
    Status=models.CharField(max_length=50)
    CreatedDate=models.CharField(blank=True, null=True, max_length=100)
    ScheduledDeadline=models.CharField(max_length=100,default=datetime.now)
    StartDate=models.CharField(blank=True, null=True, max_length=100)
    EndDate=models.CharField(blank=True, null=True, max_length=100)
    TaskPoint=models.IntegerField(default=1)
    TaskType=models.CharField(blank=True, null=True, max_length=100)
    RefId=models.CharField(blank=True, null=True, max_length=50)
    CompletionPoint=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    VerifiedBy=models.CharField(blank=True, null=True, max_length=50)
    IsRepeated = models.BooleanField(default=False)
    RepeatInterval = models.CharField(max_length=50, blank=True, null=True)
    ScheduledDays = models.CharField(max_length=50, blank=True, null=True)
    NextScheduledDate=models.DateTimeField(default=datetime.now)
    ExtraAccess=models.BooleanField(default=False)
    NeedVerification=models.BooleanField(default=True)
    AccessTo =models.TextField(blank=True, null=True)
    ClientId=models.CharField(blank=True, null=True, max_length=50)
    Interval=models.IntegerField(default=1)
    TempleteType=models.CharField(blank=True, null=True, max_length=50)
    IsTemplate=models.BooleanField(default=False)
    MarkAsClientVisit=models.BooleanField(default=False)
    CompanyId=models.CharField(max_length=50, blank=True, null=True)
    
class ProjectTaskTiming(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectTaskTimingId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectTaskId=models.CharField(blank=True, null=True, max_length=50)
    StartDate=models.CharField(blank=True, null=True, max_length=100)
    EndDate=models.CharField(blank=True, null=True, max_length=100)
    Duration=models.CharField(blank=True, null=True, max_length=50)
    Note=models.TextField(blank=True, null=True)


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

class ProjectDocument(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectDocumentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectId = models.CharField(max_length=50, blank=True, null=True)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    DocumentName = models.CharField(max_length=300, blank=True, null=True)
    Document = models.FileField(upload_to='ProjectDocuments/', null=True, blank=True)
    UploadedBy = models.CharField(max_length=50, default='Client') # Client or Staff
    UploadDate = models.DateTimeField(default=datetime.now)

class ProjectService(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ProjectServiceId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectId = models.CharField(max_length=50, blank=True, null=True)
    ServiceName = models.CharField(max_length=300, blank=True, null=True)
    Provider = models.CharField(max_length=300, blank=True, null=True)
    Cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ExpiryDate = models.DateTimeField(blank=True, null=True)
    IsActive = models.BooleanField(default=True)
    NotifyClient = models.BooleanField(default=True)
