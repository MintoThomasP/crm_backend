
from rest_framework import serializers

from app_basic.models import BusinessCategory, Country, CredentialCategory, Designation, ElementCategory, PermissionSection, ProjectScope, TempleteType, Unit, UserGroup, State, UserPermission, WorkPlace


class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ('SortId',
                  'DesignationId',
                  'Designation',
                  'CompanyId',
                  )


class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('SortId',
                  'UserGroupId',
                  'UserGroup',
                  'CompanyId',
                  'AccessTo')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('SortId',
                  'CountryId',
                  'Country',
                  )


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('SortId',
                  'StateId',
                  'CountryId',
                  'State'
                  )


class PermissionSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PermissionSection
        fields = (
            'PermissionSectionId',
            'SectionName'
        )


class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = (
            'UserPermissionId',
            'UserPermission',
            'PermissionSectionId',
            'DisplayName',
            'OrderNo'
        )


class TempleteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TempleteType
        fields = ('SortId',
                  'TempleteTypeId',
                  'TempleteType',
                  'CompanyId'
                  )


class UnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unit
        fields = ('SortId',
                  'UnitId',
                  'UnitName',
                  'Unit',
                  'CompanyId'
                  )


class WorkPlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkPlace
        fields = ('WorkPlaceId',
                  'WorkPlace',
                  'CompanyId'
                  )


class ProjectScopeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectScope
        fields = ('ProjectScopeId',
                  'ProjectScope',
                  'CompanyId'
                  )


class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = ('BusinessCategoryId',
                  'BusinessCategory',
                  'CompanyId'
                  )


class ElementCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementCategory
        fields = ('ElementCategoryId',
                  'ElementCategory',
                  'CompanyId'
                  )


class CredentialCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialCategory
        fields = ('SortId',
                  'CredentialCategoryId',
                  'CredentialCategoryName',
                  'CompanyId')
