from django.db import models
import uuid
from datetime import datetime

# Create your models here.


class Client(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId=models.CharField(max_length=50, blank=True, null=True)
    Salutation=models.CharField(max_length=5, blank=True, null=True)
    FirstName=models.CharField(max_length=300, blank=True, null=True)
    LastName=models.CharField(max_length=300, blank=True, null=True)
    CompanyName=models.CharField(max_length=300, blank=True, null=True)
    CustomerDisplayName=models.CharField(max_length=300, blank=True, null=True)
    EmailId=models.CharField(max_length=150, blank=True, null=True)
    Phone1=models.CharField(max_length=15, blank=True, null=True)
    Phone2=models.CharField(max_length=15, blank=True, null=True)
    CustomerType=models.CharField(max_length=300, blank=True, null=True)
    AdvanceAmount=models.CharField(max_length=15, blank=True, null=True, default="0")
    SetDefaultProject=models.BooleanField(default=True)
    CountryCode1=models.CharField(blank=True, null=True, max_length=10)
    CountryCode2=models.CharField(blank=True, null=True, max_length=10)
    ActiveStatus=models.BooleanField(default=True)
    PLLedger=models.JSONField(null=True,blank=True)
    BalanceSheetLedger=models.JSONField(null=True,blank=True)
    TotalWorkingHoursPerMonth=models.IntegerField(default=0)
    TotalVisitPerMonth=models.IntegerField(default=0)


class ClientOtherDetails(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientOtherDetailId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(max_length=50, blank=True, null=True)
    Currency=models.CharField(max_length=50, blank=True, null=True)
    OpeningBalance=models.CharField(max_length=15, blank=True, null=True)


class ClientDocuments(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientDocumentId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientOtherDetailId=models.CharField(max_length=50, blank=True, null=True)
    Document=models.FileField(upload_to='ClientDocuments/',null=True,blank=True)
    

class ClientAddress(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientAddressId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(max_length=50, blank=True, null=True)
    CustomerName=models.CharField(max_length=300, blank=True, null=True)
    Country=models.CharField(max_length=100, blank=True, null=True)
    City=models.CharField(max_length=100, blank=True, null=True)
    State=models.CharField(max_length=50, blank=True, null=True)
    Address1=models.TextField(blank=True, null=True)
    Address2=models.TextField(blank=True, null=True)
    ZipCode=models.CharField(max_length=20, blank=True, null=True)
    Phone=models.CharField(max_length=15, blank=True, null=True)
    FaxNumber=models.CharField(max_length=20, blank=True, null=True)    
    IsDefaultAddress=models.BooleanField(default=False)

class ContactPerson(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ContactPersonId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(max_length=50, blank=True, null=True)
    Salutation=models.CharField(max_length=5, blank=True, null=True)
    FirstName=models.CharField(max_length=300, blank=True, null=True)
    LastName=models.CharField(max_length=300, blank=True, null=True)
    EmailId=models.CharField(max_length=150, blank=True, null=True)
    Phone1=models.CharField(max_length=15, blank=True, null=True)
    Phone2=models.CharField(max_length=15, blank=True, null=True)


class ClientVisitRegister(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientVisitRegisterId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId=models.CharField(max_length=50, blank=True, null=True)
    StaffId=models.CharField(max_length=300, blank=True, null=True)
    VisitedDate=models.DateTimeField(default=datetime.now)
    Notes=models.TextField(blank=True, null=True)
