from django.db import models
import uuid
from datetime import datetime
# Create your models here.


class Designation(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    DesignationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Designation = models.CharField(max_length=300, blank=True, null=True)
    CompanyId=models.CharField(blank=True, null=True, max_length=50) 
    def __str__(self) :
        return self.Designation

class UserGroup(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    UserGroupId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserGroup = models.CharField(max_length=300, blank=True, null=True)
    AccessTo = models.TextField(blank=True, null=True)
    CompanyId=models.CharField(blank=True, null=True, max_length=50) 



class Country(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CountryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Country = models.CharField(max_length=300, blank=True, null=True)


class State(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StateId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CountryId = models.CharField(
        max_length=50, blank=True, null=True)
    State = models.CharField(max_length=300, blank=True, null=True)






class UserPermission(models.Model):
    UserPermissionId = models.AutoField(primary_key=True, editable=False)
    UserPermission = models.CharField(max_length=300, blank=True, null=True)
