from rest_framework import serializers

from app_site.models import Notification, SiteContact, SiteMessage, SiteSettings


class SiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ('SiteSettingsId',
                  'CompanyId',
                  'Address',
                  'Email1',
                  'Email2',
                  'Phone1',
                  'Phone2',
                  'WhatsappNumber',
                  'GoogleMapLink',
                  'InvoicePrefix',
                  'VendorCodePrefix',
                  'QuotationPrefix',
                  'MobilePrefix',
                  'TaxPercentage',
                  'TaxType',
                  'CurrencyType',
                  'InvoiceTemplate',
                  'MobilePattern',
                  'WhatsAppPattern',
                  'CompanySeal',
                  'Logo',
                  'PrimaryColor',
                  'SecondaryColor',
                  'FavIcon',
                  'StaffCodePrefix',
                  'DefaultMobilePrefix',
                  'BankAccount'
        )



class SaveSiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ('SiteSettingsId',
                  'CompanyId',
                  'Address',
                  'Email1',
                  'Email2',
                  'Phone1',
                  'Phone2',
                  'WhatsappNumber',
                  'GoogleMapLink',
                  'InvoicePrefix',
                  'QuotationPrefix',
                  'VendorCodePrefix',
                  'MobilePrefix',
                  'TaxPercentage',
                  'TaxType',
                  'CurrencyType',
                  'InvoiceTemplate',
                  'MobilePattern',
                  'WhatsAppPattern',
                  'PrimaryColor',
                  'SecondaryColor',
                  'StaffCodePrefix',
                  'DefaultMobilePrefix',
                  'BankAccount'        
        )



class UploadSiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ('SiteSettingsId',
                  'Logo',
                  'CompanySeal',
                  'FavIcon'
        )


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('NotificationId',
                  'Title',
                  'Message',
                  'FromUser',
                  'ToUser',
                  'CreatedDate'
        )

class SiteMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteMessage
        fields = ('SortId',
                  'SiteMessageId',
                  'CompanyId',
                  'SiteMessage',
                  'ExpiryDate'
        )


class SiteContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteContact
        fields = ('SortId',
                  'SiteContactId',
                  'Name',
                  'Email',
                  'ContactType',
                  'PhoneNumber',
                  'CompanyName',
                  'Message',
                  'Services',
                  'CompanyId'
                 
                  )