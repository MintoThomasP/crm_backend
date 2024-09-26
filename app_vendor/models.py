from django.db import models


from django.db import models
import uuid
from datetime import datetime

# Create your models here.


class Vendor(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    VendorId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId=models.CharField(max_length=50, blank=True, null=True)
    VendorCode=models.CharField(max_length=15, blank=True, null=True)
    Salutation=models.CharField(max_length=5, blank=True, null=True)
    FirstName=models.CharField(max_length=300, blank=True, null=True)
    LastName=models.CharField(max_length=300, blank=True, null=True)
    CompanyName=models.CharField(max_length=300, blank=True, null=True)
    VendorDisplayName=models.CharField(max_length=300, blank=True, null=True)
    EmailId=models.CharField(max_length=150, blank=True, null=True)
    Phone1=models.CharField(max_length=15, blank=True, null=True)
    Phone2=models.CharField(max_length=15, blank=True, null=True)
    CountryCode1=models.CharField(blank=True, null=True, max_length=10)
    CountryCode2=models.CharField(blank=True, null=True, max_length=10)
    ActiveStatus=models.BooleanField(default=True)

   





class VendorDocuments(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    VendorDocumentId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    VendorId=models.CharField(max_length=50, blank=True, null=True)
    Document=models.FileField(upload_to='VendorDocuments/',null=True,blank=True)
    DocumentName=models.CharField(max_length=300, blank=True, null=True)
    DocumentNumber=models.CharField(max_length=50, blank=True, null=True)
    

class VendorAddress(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    VendorAddressId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    VendorId=models.CharField(max_length=50, blank=True, null=True)
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

class VendorContactPerson(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ContactPersonId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    VendorId=models.CharField(max_length=50, blank=True, null=True)
    Salutation=models.CharField(max_length=5, blank=True, null=True)
    FirstName=models.CharField(max_length=300, blank=True, null=True)
    LastName=models.CharField(max_length=300, blank=True, null=True)
    EmailId=models.CharField(max_length=150, blank=True, null=True)
    Phone1=models.CharField(max_length=15, blank=True, null=True)
    Phone2=models.CharField(max_length=15, blank=True, null=True)




class VendorBankDetails(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    BankDetailId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    VendorId=models.CharField(blank=True, null=True, max_length=50)
    AccountHolderName=models.CharField(blank=True, null=True, max_length=300)
    BankName=models.CharField(blank=True, null=True, max_length=300)
    AccountNumber=models.CharField(blank=True, null=True, max_length=50)
    IFSCCode=models.CharField(blank=True, null=True, max_length=50)
    PrimaryAccount=models.BooleanField(default=False)
