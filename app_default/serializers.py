from app_default.models import Designation, TaskStatus, UserGroup, UserType
from rest_framework import serializers


class TaskStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskStatus
        fields = (
'StatusId',
'Status',
'Point',
)
        


class UserTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserType
        fields = (
'UserTypeId',
'UserType',

)
        

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ('SortId',
                  'DesignationId',
                  'Designation',
                  )
        

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('SortId',
                  'UserGroupId',
                  'UserGroup',
                  'AccessTo')