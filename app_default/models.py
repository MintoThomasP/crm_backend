from django.db import models
import uuid
from datetime import datetime

# Create your models here.

class TaskStatus(models.Model):
    StatusId=models.AutoField(primary_key=True, editable=False)
    Status=models.CharField(max_length=300, blank=True, null=True)
    Point=models.CharField(max_length=2, blank=True, null=True)
    def __str__(self) :
        return self.Status


class UserType(models.Model):
    UserTypeId = models.CharField(max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserType = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self) :
        return self.UserType



class Currency(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CurrencyId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Currency = models.CharField(max_length=300, blank=True, null=True)


class PaymentMode(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    PaymentModeId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    PaymentMode =models.CharField(max_length=300, blank=True, null=True)


class DepositTo(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    DepositToId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    DepositTo = models.CharField(max_length=300, blank=True, null=True)


class InvoiceStatus(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    InvoiceStatusId = models.AutoField(primary_key=True, editable=False)
    InvoiceStatus = models.CharField(max_length=300, blank=True, null=True)



class StaffStatus(models.Model):
    StatusId=models.AutoField(primary_key=True, editable=False)
    Status=models.CharField(max_length=300, blank=True, null=True)



class LeaveType(models.Model):
    LeaveTypeId=models.AutoField(primary_key=True, editable=False)
    LeaveType=models.CharField(max_length=300, blank=True, null=True)

class LeaveStatus(models.Model):
    StatusId=models.AutoField(primary_key=True, editable=False)
    Status=models.CharField(max_length=300, blank=True, null=True)


class CompanyDocumentType(models.Model):
    DocumentTypeId=models.AutoField(primary_key=True, editable=False)
    DocumentType=models.CharField(max_length=300, blank=True, null=True)



class SectionType(models.Model):
    SectionTypeId=models.AutoField(primary_key=True, editable=False)
    SectionType=models.CharField(max_length=300, blank=True, null=True)



class CategoryType(models.Model):
    CategoryTypeId=models.AutoField(primary_key=True, editable=False)
    CategoryType=models.CharField(max_length=300, blank=True, null=True)
    UsageType=models.CharField(max_length=300, blank=True, null=True)
    Ref=models.CharField(max_length=10, blank=True, null=True)
    OrderNo=models.IntegerField(default=0)


class ReportType(models.Model):
    ReportTypeId=models.AutoField(primary_key=True, editable=False)
    ReportType=models.CharField(max_length=300, blank=True, null=True)



class MeetingType(models.Model):
    MeetingTypeId=models.AutoField(primary_key=True, editable=False)
    MeetingType=models.CharField(max_length=300, blank=True, null=True)

class EnquiryStatus(models.Model):
    StatusId = models.AutoField(primary_key=True, editable=False)
    Status = models.CharField(max_length=300, blank=True, null=True)

class EnquiryType(models.Model):
    EnquiryTypeId=models.AutoField(primary_key=True, editable=False)
    EnquiryType=models.CharField(max_length=300, blank=True, null=True)

class FollowUpType(models.Model):
    FollowUpTypeId=models.AutoField(primary_key=True, editable=False)
    FollowUpType=models.CharField(max_length=300, blank=True, null=True)

class FollowUpStatus(models.Model):
    StatusId = models.AutoField(primary_key=True, editable=False)
    Status = models.CharField(max_length=300, blank=True, null=True)



class CountryCode(models.Model):
    CountryCodeId = models.AutoField(primary_key=True, editable=False)
    Country = models.CharField(max_length=300, blank=True, null=True)
    CountryCode = models.CharField(max_length=10, blank=True, null=True)
    RegularExpression=models.TextField(blank=True, null=True)



class ClientReference(models.Model):
    ClientReferenceId= models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Reference=models.CharField(max_length=300, blank=True, null=True)
    
class SiteContactType(models.Model):
    ContactTypeId = models.AutoField(primary_key=True, editable=False)
    ContactType= models.CharField(max_length=150, blank=True, null=True)
