from django.db import models
from datetime import datetime
import uuid

# Create your models here.


class Login(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    LoginId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserId = models.CharField(max_length=50)
    EmailId = models.CharField(max_length=150)
    UserType = models.ForeignKey(
        'app_default.UserType', on_delete=models.CASCADE)
    Password = models.CharField(max_length=300)
    Token = models.CharField(max_length=300, null=True, blank=True)
    Status = models.IntegerField(default=0)