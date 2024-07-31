from django.db import models
from datetime import datetime
import uuid
# Create your models here.

class Enquiry(models.Model):
    EnquiryId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CustomerName=models.CharField(max_length=300,null=True, blank=True)
    Description=models.TextField(null=True,blank=True)
    EnquiryType=models.CharField(max_length=50,null=True, blank=True)
    EmailId=models.CharField(max_length=150,null=True, blank=True)
    PhoneNumber=models.CharField(max_length=15,null=True, blank=True)
    Status=models.CharField(max_length=50)
    CompanyName=models.CharField(max_length=300,null=True, blank=True)
    EnquiryDate=models.CharField(max_length=50,null=True, blank=True)
    CreatedDate=models.DateTimeField(default=datetime.now)
    CreatedBy=models.CharField(max_length=50,null=True, blank=True)
    CompanyId=models.CharField(max_length=50,null=True, blank=True)




class FollowUp(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    FollowUpId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    EnquiryId = models.CharField(max_length=50,blank=True, null=True)
    UserId=models.CharField(max_length=50,blank=True, null=True)
    FollowUpType=models.CharField(max_length=50,blank=True, null=True) # Through mail or Phone
    FollowUpDateandTime=models.CharField(max_length=50,blank=True, null=True)
    Note=models.TextField(blank=True, null=True)
    ScheduledDateandTime=models.CharField(max_length=50,blank=True, null=True) #come as next entry
    ScheduledBy=models.CharField(max_length=50,blank=True, null=True)
    ReferedBy=models.CharField(max_length=50,blank=True, null=True)#Previous FollowUpId
    Status = models.CharField(max_length=100,blank=True, null=True)