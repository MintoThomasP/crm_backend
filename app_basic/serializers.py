
from rest_framework import serializers

from app_basic.models import Country, Designation, UserGroup,State, UserPermission

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
        

class UserPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPermission
        fields = (
                  'UserPermissionId',
                  'UserPermission',
                  )