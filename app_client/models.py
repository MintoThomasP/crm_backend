from django.db import models
import uuid
from datetime import datetime

# Create your models here.


class Client(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)
    Salutation = models.CharField(max_length=5, blank=True, null=True)
    FirstName = models.CharField(max_length=300, blank=True, null=True)
    LastName = models.CharField(max_length=300, blank=True, null=True)
    CompanyName = models.CharField(max_length=300, blank=True, null=True)
    CustomerDisplayName = models.CharField(
        max_length=300, blank=True, null=True)
    EmailId = models.CharField(max_length=150, blank=True, null=True)
    Phone1 = models.CharField(max_length=15, blank=True, null=True)
    Phone2 = models.CharField(max_length=15, blank=True, null=True)
    CustomerType = models.CharField(
        max_length=300, blank=True, null=True)  # business/individual
    AdvanceAmount = models.CharField(
        max_length=15, blank=True, null=True, default="0")
    SetDefaultProject = models.BooleanField(default=True)
    CountryCode1 = models.CharField(blank=True, null=True, max_length=10)
    CountryCode2 = models.CharField(blank=True, null=True, max_length=10)
    ActiveStatus = models.BooleanField(default=True)
    PLLedger = models.JSONField(null=True, blank=True)
    BalanceSheetLedger = models.JSONField(null=True, blank=True)
    TotalWorkingHoursPerMonth = models.IntegerField(default=0)
    TotalVisitPerMonth = models.IntegerField(default=0)
    # digital marketing, GoogleAds
    Reference = models.CharField(max_length=300, blank=True, null=True)
    TaxType = models.CharField(max_length=300, blank=True, null=True)
    TaxId = models.CharField(max_length=300, blank=True, null=True)
    ContactGroupId = models.CharField(max_length=50, blank=True, null=True)
    CreditLimit = models.CharField(max_length=15, blank=True, null=True, default="0.00")
    CreditLimitEnforced = models.BooleanField(default=False)


class ClientOtherDetails(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientOtherDetailId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    Currency = models.CharField(max_length=50, blank=True, null=True)
    OpeningBalance = models.CharField(max_length=15, blank=True, null=True)


class ClientDocuments(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientDocumentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(blank=True, null=True, max_length=50)
    Document = models.FileField(
        upload_to='clientdocuments/', null=True, blank=True)
    DocumentName = models.CharField(blank=True, null=True, max_length=300)
    ImageType = models.CharField(blank=True, null=True, max_length=300)
    DocumentNumber = models.CharField(blank=True, null=True, max_length=300)
    IssuedOn = models.CharField(blank=True, null=True, max_length=50)
    ExpiryDate = models.CharField(blank=True, null=True, max_length=50)
    Comment = models.TextField(blank=True, null=True)
    DocumentType = models.CharField(blank=True, null=True, max_length=50, default="Other")


class ClientReminder(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientReminderId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(blank=True, null=True, max_length=50)
    Title = models.CharField(blank=True, null=True, max_length=300)
    Description = models.TextField(blank=True, null=True)
    ReminderType = models.CharField(blank=True, null=True, max_length=50)
    TargetDate = models.DateTimeField(help_text="The due date for the action.")
    RemindBefore = models.PositiveIntegerField(
        default=2, help_text="Days before target_date to remind")
    IsRecurring = models.BooleanField(default=True)
    RecurrencePeriod = models.CharField(max_length=50)


class ClientAddress(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientAddressId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    CustomerName = models.CharField(max_length=300, blank=True, null=True)
    Country = models.CharField(max_length=100, blank=True, null=True)
    City = models.CharField(max_length=100, blank=True, null=True)
    State = models.CharField(max_length=50, blank=True, null=True)
    Address1 = models.TextField(blank=True, null=True)
    Address2 = models.TextField(blank=True, null=True)
    ZipCode = models.CharField(max_length=20, blank=True, null=True)
    Phone = models.CharField(max_length=15, blank=True, null=True)
    FaxNumber = models.CharField(max_length=20, blank=True, null=True)
    IsDefaultAddress = models.BooleanField(default=False)
    Status = models.IntegerField(default=1)  # 1=Active,2=Inactive


class ContactPerson(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ContactPersonId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    Salutation = models.CharField(max_length=5, blank=True, null=True)
    FirstName = models.CharField(max_length=300, blank=True, null=True)
    LastName = models.CharField(max_length=300, blank=True, null=True)
    Designation = models.CharField(max_length=300, blank=True, null=True)
    EmailId = models.CharField(max_length=150, blank=True, null=True)
    Phone1 = models.CharField(max_length=15, blank=True, null=True)
    Phone2 = models.CharField(max_length=15, blank=True, null=True)


class ClientVisitRegister(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ClientVisitRegisterId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    StaffId = models.CharField(max_length=300, blank=True, null=True)
    VisitedDate = models.DateTimeField(default=datetime.now)
    Notes = models.TextField(blank=True, null=True)


class ClientBankDetails(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    BankDetailId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ClientId = models.CharField(blank=True, null=True, max_length=50)
    AccountHolderName = models.CharField(blank=True, null=True, max_length=300)
    BankName = models.CharField(blank=True, null=True, max_length=300)
    AccountNumber = models.CharField(blank=True, null=True, max_length=50)
    IFSCCode = models.CharField(blank=True, null=True, max_length=50)
    PrimaryAccount = models.BooleanField(default=False)


class Opportunity(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    OpportunityId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    Title = models.CharField(max_length=300, blank=True, null=True)
    Stage = models.CharField(max_length=50, default='qualification')
    WinProbability = models.IntegerField(default=50)
    ExpectedValue = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    CloseDate = models.CharField(max_length=50, blank=True, null=True)
    AssignedStaffId = models.CharField(max_length=50, blank=True, null=True)


class SupportTicket(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    TicketId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    Subject = models.CharField(max_length=300, blank=True, null=True)
    Status = models.CharField(max_length=50, default='open')
    Priority = models.CharField(max_length=20, default='medium')
    SlaDeadline = models.CharField(max_length=50, blank=True, null=True)
    AssignedStaffId = models.CharField(max_length=50, blank=True, null=True)


class ContactGroup(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    GroupId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    GroupName = models.CharField(max_length=150)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)
    TaxProfile = models.CharField(max_length=100, blank=True, null=True)
    DiscountPercent = models.CharField(max_length=15, blank=True, null=True, default="0.00")
    PricingTier = models.CharField(max_length=50, blank=True, null=True, default="Standard")


class InteractionLog(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    InteractionId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)
    ClientId = models.CharField(max_length=50, blank=True, null=True)
    Type = models.CharField(max_length=50, default='Call') # Call, Email, Meeting, Note
    Summary = models.CharField(max_length=300, blank=True, null=True)
    Details = models.TextField(blank=True, null=True)
    InteractionDate = models.DateTimeField(default=datetime.now)
    StaffId = models.CharField(max_length=50, blank=True, null=True)


