from app_client.models import Client, ClientAddress, ClientBankDetails, ClientDocuments, ClientOtherDetails, ClientReminder, ClientVisitRegister, ContactPerson
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            'SortId',
            'ClientId',
            'CompanyId',
            'Salutation',
            'FirstName',
            'LastName',
            'CompanyName',
            'CustomerDisplayName',
            'EmailId',
            'Phone1',
            'Phone2',
            'CustomerType',
            'AdvanceAmount',
            'SetDefaultProject',
            'CountryCode1',
            'CountryCode2',
            'ActiveStatus',
            'PLLedger',
            'BalanceSheetLedger',
            'TotalWorkingHoursPerMonth',
            'TotalVisitPerMonth',
            'Reference'
        )


class ClientOtherDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientOtherDetails
        fields = (
            'SortId',
            'ClientOtherDetailId',
            'ClientId',
            'Currency',
            'OpeningBalance'
        )


class ClientReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientReminder
        fields = (
            'SortId',
            'ClientReminderId',
            'ClientId',
            'Title',
            'Description',
            'ReminderType',
            'TargetDate',
            'RemindBefore',
            'sRecurring',
            'RecurrencePeriod'
        )


class ClientDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDocuments
        fields = (
            'SortId',
            'ClientDocumentId',
            'ClientId',
            'Document',
            'DocumentName',
            'DocumentNumber',
            'ImageType',
            'Comment',
            'ExpiryDate',
            'IssuedOn'
        )


class ClientAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAddress
        fields = (
            'SortId',
            'ClientAddressId',
            'ClientId',
            'CustomerName',
            'Country',
            'City',
            'State',
            'Address1',
            'Address2',
            'ZipCode',
            'Phone',
            'FaxNumber',
            'IsDefaultAddress'

        )


class ContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactPerson
        fields = (
            'SortId',
            'ContactPersonId',
            'ClientId',
            'Salutation',
            'FirstName',
            'LastName',
            'Designation',
            'EmailId',
            'Phone1',
            'Phone2'
        )


class ClientVisitRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientVisitRegister
        fields = (
            'SortId',
            'ClientVisitRegisterId',
            'ClientId',
            'StaffId',
            'VisitedDate',
            'Notes'
        )


class ClientBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientBankDetails
        fields = ('SortId',
                  'BankDetailId',
                  'ClientId',
                  'AccountHolderName',
                  'BankName',
                  'AccountNumber',
                  'IFSCCode',
                  'PrimaryAccount'
                  )
