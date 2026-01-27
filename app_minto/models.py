from django.db import models
from datetime import datetime
import uuid


class Todo(models.Model):
    
    TodoId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserId = models.CharField(blank=True, null=True, max_length=50)
    Title=models.TextField(blank=True, null=True)
    CreatedDate=models.DateTimeField(default=datetime.now)
    ScheduledOn=models.CharField(blank=True, null=True, max_length=150)
    IsCompleted=models.BooleanField(default=False)
   