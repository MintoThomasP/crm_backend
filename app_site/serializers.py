from rest_framework import serializers

from app_site.models import Notification, SiteSettings


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
                  'QuotationPrefix',
                  'MobilePrefix',
                  'TaxPercentage',
                  'TaxType',
                  'CurrencyType',
                  'InvoiceTemplate',
                  'MobilePattern',
                  'WhatsAppPattern',
                  'Logo',
                  'PrimaryColor',
                  'SecondaryColor',
                  'FavIcon'
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
                  'MobilePrefix',
                  'TaxPercentage',
                  'TaxType',
                  'CurrencyType',
                  'InvoiceTemplate',
                  'MobilePattern',
                  'WhatsAppPattern',
                  'PrimaryColor',
                  'SecondaryColor',          
        )



class UploadSiteSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteSettings
        fields = ('SiteSettingsId',
                  'Logo',
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
