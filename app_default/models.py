from django.db import models
import uuid
from datetime import datetime

# Create your models here.

class TaskStatus(models.Model):
    StatusId=models.AutoField(primary_key=True, editable=False)
    Status=models.CharField(max_length=300, blank=True, null=True)
    Point=models.CharField(max_length=2, blank=True, null=True)
    def __str__(self) :
        return self.Status


class UserType(models.Model):
    UserTypeId = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserType = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self) :
        return self.UserType

class Designation(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    DesignationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Designation = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self) :
        return self.Designation

class UserGroup(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    UserGroupId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserGroup = models.CharField(max_length=300, blank=True, null=True)
    AccessTo = models.TextField(blank=True, null=True)