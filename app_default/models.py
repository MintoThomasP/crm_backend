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

class Designation(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    DesignationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Designation = models.CharField(max_length=300, blank=True, null=True)
    def __str__(self) :
        return self.Designation

class UserGroup(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    UserGroupId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserGroup = models.CharField(max_length=300, blank=True, null=True)
    AccessTo = models.TextField(blank=True, null=True)

class City(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CityId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    StateId = models.CharField(
        max_length=50, blank=True, null=True)
    City = models.CharField(max_length=300, blank=True, null=True)

class Country(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CountryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Country = models.CharField(max_length=300, blank=True, null=True)


class State(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    StateId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CountryId = models.CharField(
        max_length=50, blank=True, null=True)
    State = models.CharField(max_length=300, blank=True, null=True)

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