from django.db import models
import uuid
from datetime import datetime

class ClientPortalAccess(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientPortalAccessId = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50) 
    LoginId = models.CharField(max_length=50)  
    IsActive = models.BooleanField(default=True)

class ClientDocumentUpload(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientDocumentUploadId = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50)
    ProjectId = models.CharField(max_length=50, null=True, blank=True)
    Document = models.FileField(upload_to='client_portal_documents/', null=True, blank=True)
    DocumentName = models.CharField(max_length=300, blank=True, null=True)
    UploadedAt = models.DateTimeField(default=datetime.now)
    Notes = models.TextField(blank=True, null=True)

class ServiceExpiryAlert(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ServiceExpiryAlertId = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50)
    ProjectId = models.CharField(max_length=50, null=True, blank=True)
    ServiceName = models.CharField(max_length=300)
    ExpiryDate = models.DateTimeField()
    IsAlertSent = models.BooleanField(default=False)
