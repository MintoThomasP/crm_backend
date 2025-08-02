from django.db import models
import uuid
from datetime import datetime
# Create your models here.


class Designation(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    DesignationId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    Designation = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)

    def __str__(self):
        return self.Designation


class UserGroup(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    UserGroupId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UserGroup = models.CharField(max_length=300, blank=True, null=True)
    AccessTo = models.TextField(blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)


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


class PermissionSection(models.Model):
    PermissionSectionId = models.AutoField(primary_key=True, editable=False)
    SectionName = models.CharField(max_length=300, blank=True, null=True)


class UserPermission(models.Model):
    UserPermissionId = models.AutoField(primary_key=True, editable=False)
    UserPermission = models.CharField(max_length=300, blank=True, null=True)
    PermissionSectionId = models.CharField(
        max_length=10, blank=True, null=True)
    DisplayName = models.CharField(max_length=300, blank=True, null=True)
    OrderNo = models.IntegerField(default=1)


class TempleteType(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    TempleteTypeId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    TempleteType = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)


class Unit(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    UnitId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    UnitName = models.CharField(max_length=300, blank=True, null=True)
    Unit = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)


class WorkPlace(models.Model):
    WorkPlaceId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    WorkPlace = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)


class ProjectScope(models.Model):
    ProjectScopeId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ProjectScope = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)


class BusinessCategory(models.Model):
    BusinessCategoryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    BusinessCategory = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)


class ElementCategory(models.Model):
    ElementCategoryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    ElementCategory = models.CharField(max_length=300, blank=True, null=True)
    CompanyId = models.CharField(max_length=50, blank=True, null=True)


class CredentialCategory(models.Model):
    SortId = models.DateTimeField(editable=False, default=datetime.now)
    CredentialCategoryId = models.CharField(
        max_length=50, primary_key=True, default=uuid.uuid4, editable=False)
    CredentialCategoryName = models.CharField(
        max_length=300, blank=True, null=True)
    CompanyId = models.CharField(blank=True, null=True, max_length=50)
