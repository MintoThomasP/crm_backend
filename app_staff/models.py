from django.db import models
from datetime import datetime
import uuid

# Create your models here.

class Staff(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StaffId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StaffCode=models.CharField(max_length=15, unique=True, editable=False)
    StaffName = models.CharField(blank=True, null=True, max_length=300)
    PhoneNumber = models.CharField(blank=True, null=True, max_length=30)
    Gender = models.CharField(blank=True, null=True, max_length=30)
    DOB=models.DateTimeField(null=True, default=None)
    EmailId = models.CharField(blank=True, null=True, max_length=150)
    PermanentAddress = models.TextField(blank=True, null=True)
    JoinedOn=models.DateTimeField(default=datetime.now)
    QrCode=models.ImageField(upload_to='qr_codes/',null=True,blank=True)
    Salary=models.CharField(blank=True, null=True, max_length=15)
    Designation=models.CharField(blank=True, null=True, max_length=300)
    UserGroup=models.CharField(blank=True, null=True, max_length=300)
    CurrentAddress=models.TextField(blank=True, null=True)
    ProfilePhoto=models.ImageField(upload_to='profiles/',null=True,blank=True)

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


