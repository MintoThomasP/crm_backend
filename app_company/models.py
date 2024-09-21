from django.db import models
import uuid
from datetime import datetime
# Create your models here.




class Company(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CompanyId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyName=models.CharField(max_length=300, blank=True, null=True)
    EmailId=models.CharField(max_length=150, blank=True, null=True)
    Website=models.TextField(blank=True, null=True)
    RegisteredOn=models.CharField(max_length=150, blank=True, null=True)
    Address=models.TextField(blank=True, null=True)
    UserGroup=models.CharField(blank=True, null=True, max_length=300)
    ActiveStatus=models.BooleanField(default=True)


class CompanyDocuments(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CompanyDocumentId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId=models.CharField(max_length=50, blank=True, null=True)
    DocumentName=models.CharField(max_length=50, blank=True, null=True)
    DocumentType=models.CharField(max_length=300, blank=True, null=True)
    Document=models.FileField(upload_to='CompanyDocuments/',null=True,blank=True)
    ExpiryDate=models.CharField(max_length=150, blank=True, null=True)

