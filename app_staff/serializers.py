from app_staff.models import Staff
from rest_framework import serializers


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('SortId',
'StaffId',
'StaffName',
'PhoneNumber',
'Gender',
'DOB',
'EmailId',
'Address',
'JoinedOn')