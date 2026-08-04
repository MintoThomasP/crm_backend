from app_vendor.models import Vendor, VendorAddress, VendorBankDetails, VendorContactPerson, VendorDocuments, VendorBill
from rest_framework import serializers


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = (
            'SortId',
'VendorId',
'CompanyId',
'VendorCode',
'Salutation',
'FirstName',
'LastName',
'CompanyName',
'VendorDisplayName',
'EmailId',
'Phone1',
'Phone2',
'CountryCode1',
'CountryCode2',
'ActiveStatus'
)
        

        

class VendorDocumentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorDocuments
        fields = (
            'SortId',
            'VendorDocumentId',
'VendorId',
'Document',
'DocumentName',
'DocumentNumber'

)
        

class VendorAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAddress
        fields = (
           'SortId',
'VendorAddressId',
'VendorId',
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
        


class VendorContactPersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorContactPerson
        fields = (
'SortId',
'ContactPersonId',
'VendorId',
'Salutation',
'FirstName',
'LastName',
'EmailId',
'Phone1',
'Phone2'
)


        


        
class VendorBankDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBankDetails
        fields = ('SortId',
'BankDetailId',
'VendorId',
'AccountHolderName',
'BankName',
'AccountNumber',
'IFSCCode',
'PrimaryAccount'
)
  

class VendorBillSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorBill
        fields = '__all__'