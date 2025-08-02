from django.db import models
from datetime import datetime
import uuid
# Create your models here.


class Category(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CategoryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    RefId = models.CharField(blank=True, null=True, max_length=50)
    Category = models.CharField(blank=True, null=True, max_length=300)
    SectionType = models.CharField(
        blank=True, null=True, max_length=300)  # Product,Finance
    CategoryType = models.CharField(
        blank=True, null=True, max_length=300)  # data from default table
    ActiveStatus = models.BooleanField(default=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)


class Report(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ReportId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    # P&L Report=1, Balance Sheet=2
    ReportType = models.CharField(max_length=50)
    Month = models.CharField(max_length=15)
    Year = models.CharField(max_length=10)
    ClientId = models.CharField(max_length=50)
    CategoryId = models.CharField(max_length=50)
    Amount = models.CharField(blank=True, null=True, max_length=15)
    Comment = models.TextField(blank=True, null=True)
    OrderNo = models.IntegerField(default=1)
    Level = models.IntegerField(default=1)  # its the level of category
    Status = models.IntegerField(default=0)
    InDraft = models.IntegerField(default=0)  # 1 is draft


class ReportRefFile(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    ReportRefFileId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ReportRefFile = models.FileField(
        upload_to='ReportRefFile/', null=True, blank=True)
    ReportId = models.ForeignKey(
        Report, on_delete=models.CASCADE, related_name='images')
    OrderNo = models.IntegerField(default=1)
