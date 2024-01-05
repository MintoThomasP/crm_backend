from django.db import models
from datetime import datetime
import uuid

# Create your models here.

class Staff(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StaffId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffName = models.CharField(blank=True, null=True, max_length=300)
    PhoneNumber = models.CharField(blank=True, null=True, max_length=30)
    Gender = models.CharField(blank=True, null=True, max_length=30)
    DOB=models.DateTimeField(null=True, default=None)
    EmailId = models.CharField(blank=True, null=True, max_length=150)
    Address = models.TextField(blank=True, null=True)
    JoinedOn=models.DateTimeField(default=datetime.now)
