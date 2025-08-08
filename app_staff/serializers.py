from app_staff.models import LeaveApplication, MoveOnRegister, SalarySlip, Staff, StaffBankDetails, StaffDocuments, StaffGuardian
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
                  'ProfilePhoto',
                  'BankAccount',
                  'CountryCode',
                  'MedicalLeave',
                  'CasualLeave',
                  'AnnualLeave'
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
                  'CurrentAddress',
                  'BankAccount',
                  'CountryCode',
                  'MedicalLeave',
                  'CasualLeave',
                  'AnnualLeave')


class UpdateStaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = (
            'StaffId',
            'ProfilePhoto'
        )


class StaffPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = ('SortId',
                  'StaffId',
                  'StaffName',
                  'StaffCode',
                  'CompanyId',
                  'Designation'
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
                  'DocumentNumber',
                  'ImageType',
                  'Comment',
                  'ExpiryDate',
                  'IssuedOn'
                  )


class SaveStaffDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffDocuments
        fields = ('SortId',
                  'StaffDocumentId',
                  'StaffId',
                  'DocumentName',
                  'ImageType',
                  'Comment',
                  'DocumentNumber',
                  'ExpiryDate',
                  'IssuedOn'

                  )


class UploadStaffDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffDocuments
        fields = (
            'StaffDocumentId',
            'Document',

        )


class StaffBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffBankDetails
        fields = ('SortId',
                  'BankDetailId',
                  'StaffId',
                  'AccountHolderName',
                  'BankName',
                  'AccountNumber',
                  'IFSCCode',
                  'PrimaryAccount'
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
                  'Status',
                  'CompanyId',
                  'NoOfDays'

                  )


class SalarySlipSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalarySlip
        fields = (
            'SortId',
            'SalarySlipId',
            'StaffId',
            'Year',
            'Month',
            'BasicPay',
            'ConveyanceAllowance',
            'MedicalAllowance',
            'OtherAllowance',
            'AppreciationBonus',
            'TotalWorkingDays',
            'LOP',
            'PaidDays',
            'Leave',
            'GrossPay',
            'BankAccount'
        )


class MoveOnRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoveOnRegister
        fields = ('SortId',
                  'StaffId',
                  'MoveOnRegisterId',
                  'MoveOnReason',
                  'Notes',
                  'MoveOutDateTime',
                  'MoveInDateTime',

                  )
