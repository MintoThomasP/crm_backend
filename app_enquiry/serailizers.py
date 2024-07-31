from rest_framework import serializers

from app_enquiry.models import Enquiry, FollowUp

class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = (
'EnquiryId',
'CustomerName',
'Description',
'EnquiryType',
'EmailId',
'PhoneNumber',
'Status',
'CompanyName',
'EnquiryDate',
'CreatedDate',
'CreatedBy',
'CompanyId')
        


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
            'ScheduledBy',
            'ReferedBy',
            'Status'
        )