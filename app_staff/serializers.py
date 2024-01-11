from app_staff.models import Staff, StaffGuardian
from rest_framework import serializers


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('SortId',
'StaffId',
'StaffName',
'StaffCode',
'PhoneNumber',
'Gender',
'DOB',
'EmailId',
'PermanentAddress',
'JoinedOn',
'QrCode',
'Salary',
'Designation',
'UserGroup',
'CurrentAddress'
)
        

class SaveStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('SortId',
'StaffId',
'StaffName',
'StaffCode',
'PhoneNumber',
'Gender',
'DOB',
'EmailId',
'PermanentAddress',
'JoinedOn',
'Salary',
'Designation',
'UserGroup',
'CurrentAddress')
        


class StaffGuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffGuardian
        fields = ('SortId',
'StaffGuardianId',
'StaffId',
'GuardianName',
'PhoneNumber',
'EmailId',
'Relation',
)