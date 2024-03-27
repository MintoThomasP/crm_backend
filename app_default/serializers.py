
from app_default.models import Country, Currency, DepositTo, Designation, InvoiceStatus, PaymentMode, State, TaskStatus, UserGroup, UserType
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
        

class DesignationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Designation
        fields = ('SortId',
                  'DesignationId',
                  'Designation',
                  )
        

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ('SortId',
                  'UserGroupId',
                  'UserGroup',
                  'AccessTo')
        




class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('SortId',
                  'CountryId',
                  'Country',
                  )
        
        
class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ('SortId',
                  'StateId',
                  'CountryId',
                  'State'
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