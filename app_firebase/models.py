from django.db import models
from datetime import datetime
import uuid

from django.db import models
from django.conf import settings


class DeviceToken(models.Model):
    DeviceTokenId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserId = models.CharField(max_length=200, blank=True, null=True)
    Token = models.CharField(max_length=512, unique=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    Active = models.BooleanField(default=True)
    UserType = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.UserId} - {self.Token[:20]}..."
