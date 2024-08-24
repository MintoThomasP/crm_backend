from django.db import models
from datetime import datetime
import uuid
# Create your models here.



class Credentials(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CredentialId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId=models.CharField(blank=True, null=True, max_length=50)
    Name=models.CharField(blank=True, null=True, max_length=300)
    LoginURL=models.TextField(blank=True, null=True)
    UserName=models.CharField(blank=True, null=True, max_length=300)
    Password=models.CharField(blank=True, null=True, max_length=300)
    AccessTo=models.TextField(blank=True, null=True)
    ClientId=models.CharField(blank=True, null=True, max_length=50)
    UserId=models.CharField(blank=True, null=True, max_length=50)