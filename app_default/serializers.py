
from xml.dom.minidom import DocumentType
from app_default.models import CategoryType, ClientReference, CompanyDocumentType, CountryCode, Currency, DepositTo, EnquiryStatus, EnquirySource, FollowUpStatus, FollowUpType, InvoiceStatus, LeaveStatus, LeaveType, MeetingType, PaymentMode, ReportType, SectionType, ServiceType, SiteContactType, StaffStatus, TaskStatus, UserType
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
        


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ('SortId',
                  'CurrencyId',
                  'Currency',
                  
                  )
        

class PaymentModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMode
        fields = ('SortId',
                  'PaymentModeId',
                  'PaymentMode',
                  )
        

class DepositToSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositTo
        fields = ('SortId',
                  'DepositToId',
                  'DepositTo',
                  )
        
class InvoiceStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceStatus
        fields = ('SortId',
                  'InvoiceStatusId',
                  'InvoiceStatus',
                  )
        

class StaffStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffStatus
        fields = (
'StatusId',
'Status'
)
  

class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = (
'LeaveTypeId',
'LeaveType'
)
  

class LeaveStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveStatus
        fields = (
'StatusId',
'Status'
)
        



class CompanyDocumentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyDocumentType
        fields = (
'DocumentTypeId',
'DocumentType'
)
        



class SectionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionType
        fields = (
'SectionTypeId',
'SectionType'
)
        
class CategoryTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryType
        fields = (
'CategoryTypeId',
'CategoryType',
'UsageType',
'Ref',
'SectionType',
'OrderNo'
)
        

class ReportTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportType
        fields = (
'ReportTypeId',
'ReportType'
)
        
class MeetingTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingType
        fields = (
'MeetingTypeId',
'MeetingType'
)
        
class EnquirySourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquirySource
        fields = (
'EnquirySourceId',
'EnquirySource'
)
class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = (
'ServiceTypeId',
'ServiceType'
)

class FollowUpTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpType
        fields = (
'FollowUpTypeId',
'FollowUpType'
)
             

class FollowUpStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUpStatus
        fields = (
            'StatusId',
            'Status',
        )

class EnquiryStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = EnquiryStatus
        fields = (
            'StatusId',
            'Status',
        )


class CountryCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CountryCode
        fields = (
            'CountryCodeId',
            'Country',
            'CountryCode',
            'RegularExpression'
        )



class ClientReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientReference
        fields = ('ClientReferenceId',
                  'Reference',
                  
                  )
class SiteContactTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContactType
        fields = (
            'ContactTypeId','ContactType'
        )
