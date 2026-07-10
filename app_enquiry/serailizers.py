from rest_framework import serializers

from app_enquiry.models import Enquiry, FollowUp

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = (
'EnquiryId',
'CustomerName',
'Description',
'EnquirySource',
'EmailId',
'PhoneNumber',
'Status',
'CompanyName',
'EnquiryDate',
'CreatedDate',
'CreatedBy',
'CompanyId',
'CountryCode',
'ServiceType',
'LeadScore',
'OpportunityId')

        


class FollowUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = (
            'SortId',
            'FollowUpId',
            'EnquiryId',
            'UserId',
            'FollowUpType',
            'FollowUpDateandTime',
            'Note',
            'ScheduledDateandTime',
            'ScheduledTo',
            'ReferedBy',
            'Status'
        )