from django.db import models
from datetime import datetime
import uuid

# Create your models here.

class Staff(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StaffId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffCode=models.CharField(max_length=15, unique=True, editable=False)
    CompanyId=models.CharField(blank=True, null=True, max_length=50)
    StaffName = models.CharField(blank=True, null=True, max_length=300)
    PhoneNumber = models.CharField(blank=True, null=True, max_length=30)
    Gender = models.CharField(blank=True, null=True, max_length=30)
    DOB=models.CharField(blank=True, null=True, max_length=100)
    EmailId = models.CharField(blank=True, null=True, max_length=150)
    PermanentAddress = models.TextField(blank=True, null=True)
    JoinedOn=models.CharField(blank=True, null=True, max_length=100)
    QrCode=models.ImageField(upload_to='qr_codes/',null=True,blank=True)
    Salary=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    Designation=models.CharField(blank=True, null=True, max_length=50)
    UserGroup=models.CharField(blank=True, null=True, max_length=300)
    UserType=models.CharField(blank=True, null=True, max_length=50)
    CurrentAddress=models.TextField(blank=True, null=True)
    ProfilePhoto=models.ImageField(upload_to='profiles/',null=True,blank=True)
    LeavingDate=models.CharField(blank=True, null=True, max_length=100)
    Status=models.IntegerField(default=1)
    FCMToken=models.CharField(blank=True, null=True, max_length=300)
    BankAccount=models.TextField(blank=True, null=True)
    CountryCode=models.CharField(blank=True, null=True, max_length=10)

    def save(self, *args, **kwargs):
        if not self.StaffCode or self.StaffCode == 'CS-E-1':
            self.StaffCode = self.generate_StaffCode()
        super(Staff, self).save(*args, **kwargs)

    def generate_StaffCode(self):
        last_staff = Staff.objects.order_by('-SortId').first()
        if last_staff:
            last_number = int(last_staff.StaffCode.split('-')[-1])
            new_number = last_number + 1
        else:
            new_number = 1  # Starting number
        return f'CS-E-{new_number:03d}'
    


class StaffGuardian(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StaffGuardianId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffId=models.CharField(blank=True, null=True, max_length=50)
    GuardianName=models.CharField(blank=True, null=True, max_length=300)
    PhoneNumber=models.CharField(blank=True, null=True, max_length=12)
    EmailId=models.CharField(blank=True, null=True, max_length=150)
    Relation=models.CharField(blank=True, null=True, max_length=300)


class StaffDocuments(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StaffDocumentId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffId=models.CharField(blank=True, null=True, max_length=50)
    Document=models.FileField(upload_to='staffdocuments/',null=True,blank=True)
    DocumentName=models.CharField(blank=True, null=True, max_length=300)
    Comment=models.TextField(blank=True, null=True)



class LeaveApplication(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    LeaveApplicationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffId=models.CharField(blank=True, null=True, max_length=50)
    Subject=models.CharField(blank=True, null=True, max_length=300)
    Description=models.TextField(blank=True, null=True)
    AppliedOn=models.CharField(blank=True, null=True, max_length=100)
    LeaveFrom=models.CharField(blank=True, null=True, max_length=100)
    LeaveTo=models.CharField(blank=True, null=True, max_length=100)
    LeaveType=models.CharField(blank=True, null=True, max_length=100)
    Status=models.CharField(blank=True, null=True, max_length=100)
    CompanyId=models.CharField(blank=True, null=True, max_length=50)
    NoOfDays=models.DecimalField(max_digits=10, decimal_places=2, default=0)



class SalarySlip(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    SalarySlipId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffId=models.CharField(blank=True, null=True, max_length=50)
    Year=models.IntegerField()
    Month=models.IntegerField()
    BasicPay=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ConveyanceAllowance=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    MedicalAllowance=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    OtherAllowance=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    AppreciationBonus=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    TotalWorkingDays=models.IntegerField()
    LOP=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    PaidDays=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Leave=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    GrossPay=models.DecimalField(max_digits=10, decimal_places=2, default=0)
    BankAccount=models.TextField(blank=True, null=True)



class MoveOnRegister(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    MoveOnRegisterId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffId=models.CharField(blank=True, null=True, max_length=50)
    MoveOnReason=models.CharField(blank=True, null=True, max_length=50)
    Notes=models.TextField(blank=True, null=True)
    MoveOutDateTime=models.CharField(max_length=100,blank=True, null=True)
    MoveInDateTime=models.CharField(max_length=100,blank=True, null=True)
