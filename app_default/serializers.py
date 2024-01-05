from app_default.models import TaskStatus, UserType
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