from django.db import models
import uuid

# Create your models here.

class TaskStatus(models.Model):
    StatusId=models.AutoField(primary_key=True, editable=False)
    Status=models.CharField(max_length=300, blank=True, null=True)
    Point=models.CharField(max_length=2, blank=True, null=True)


class UserType(models.Model):
    UserTypeId = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserType = models.CharField(max_length=300, blank=True, null=True)