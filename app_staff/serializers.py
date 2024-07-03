from app_staff.models import LeaveApplication, Staff, StaffDocuments, StaffGuardian
from rest_framework import serializers


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('SortId',
'StaffId',
'StaffName',
'StaffCode',
'CompanyId',
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
'UserType',
'CurrentAddress',
'LeavingDate',
'Status',
'ProfilePhoto'
)
        

class SaveStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('SortId',
'StaffId',
'StaffName',
'StaffCode',
'CompanyId',
'PhoneNumber',
'Gender',
'DOB',
'EmailId',
'PermanentAddress',
'JoinedOn',
'Salary',
'Designation',
'UserGroup',
'UserType',
'LeavingDate',
'Status',
'CurrentAddress')
        


class UpdateStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = (
'StaffId',
'ProfilePhoto'
)


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
        

class StaffDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffDocuments
        fields = ('SortId',
'StaffDocumentId',
'StaffId',
'Document',
'DocumentName',
'Comment',

)
        

class SaveStaffDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffDocuments
        fields = ('SortId',
'StaffDocumentId',
'StaffId',
'DocumentName',
'Comment',

)
        
class UploadStaffDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffDocuments
        fields = (
'StaffDocumentId',
'Document',

)
        

class LeaveApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApplication
        fields = ('SortId',
'LeaveApplicationId',
'StaffId',
'Subject',
'Description',
'AppliedOn',
'LeaveFrom',
'LeaveTo',
'LeaveType',
'Status'

)