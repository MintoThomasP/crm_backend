from django.db import models
from datetime import datetime
import uuid
# Create your models here.




class Category(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CategoryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    RefId=models.CharField(blank=True, null=True, max_length=50)
    Category=models.CharField(blank=True, null=True, max_length=300)
    SectionType=models.CharField(blank=True, null=True, max_length=300) # Product,Finance
    CategoryType=models.CharField(blank=True, null=True, max_length=300)# data from default table
    ActiveStatus=models.BooleanField(default=True)


class Report(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ReportId=models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ReportType=models.CharField(max_length=50)  #P&L Report=1, Balance Sheet=2
    Month=models.CharField(max_length=15)
    Year=models.CharField(max_length=10)
    ClientId=models.CharField(max_length=50)
    CategoryId=models.CharField(max_length=50)
    Amount=models.CharField(blank=True, null=True, max_length=15)
    Comment=models.TextField(blank=True, null=True)
    OrderNo=models.IntegerField(default=1)
    Level=models.IntegerField(default=1)#its the level of category

