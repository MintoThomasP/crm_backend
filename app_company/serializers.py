from rest_framework import serializers

from app_company.models import Company, CompanyBankDetails, CompanyDocuments


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            'SortId',
            'CompanyId',
            'CompanyName',
            'EmailId',
            'Website',
            'RegisteredOn',
            'Address',
            'Country',
            'State',
            'UserGroup',
            'ActiveStatus'
        )


class CompanyDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocuments
        fields = (
            'SortId',
            'CompanyDocumentId',
            'CompanyId',
            'DocumentName',
            'DocumentType',
            'Document',
            'ExpiryDate',
            'DocumentNumber'
        )


class SaveCompanyDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocuments
        fields = (
            'SortId',
            'CompanyDocumentId',
            'CompanyId',
            'DocumentName',
            'DocumentType',
            'ExpiryDate',
            'DocumentNumber'
        )


class UploadCompanyDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocuments
        fields = (

            'CompanyDocumentId',
            'Document',
        )


class CompanyBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyBankDetails
        fields = ('SortId',
                  'BankDetailId',
                  'CompanyId',
                  'AccountHolderName',
                  'BankName',
                  'AccountNumber',
                  'IFSCCode',
                  'PrimaryAccount'
                  )
