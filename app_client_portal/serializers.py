from rest_framework import serializers
from .models import ClientPortalAccess, ClientDocumentUpload, ServiceExpiryAlert

class ClientPortalAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientPortalAccess
        fields = '__all__'

class ClientDocumentUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientDocumentUpload
        fields = '__all__'

class ServiceExpiryAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceExpiryAlert
        fields = '__all__'
