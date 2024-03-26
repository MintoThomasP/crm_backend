from app_client.models import Client, ClientAddress, ClientDocuments, ClientOtherDetails, ContactPerson
from rest_framework import serializers


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = (
            'SortId',
'ClientId',
'Salutation',
'FirstName',
'LastName',
'CompanyName',
'CustomerDisplayName',
'EmailId',
'Phone1',
'Phone2',
'CustomerType'
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
        

class ClientDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDocuments
        fields = (
            'SortId',
            'ClientDocumentId',
'ClientOtherDetailId',
'Document',

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
'EmailId',
'Phone1',
'Phone2'
)