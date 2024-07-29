from rest_framework import serializers

from app_company.models import Company, CompanyDocuments


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
            'UserGroup'
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
            'ExpiryDate'
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
            'ExpiryDate'
        )
class UploadCompanyDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocuments
        fields = (
           
            'CompanyDocumentId',
            'Document',
        )