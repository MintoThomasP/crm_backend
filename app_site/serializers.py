from rest_framework import serializers

from app_site.models import SiteSettings


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
                  'WhatsAppPattern'
        )