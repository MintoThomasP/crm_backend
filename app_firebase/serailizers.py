from rest_framework import serializers
from .models import DeviceToken


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ['DeviceTokenId', 'UserId', 'Token', 'Active', 'CreatedAt']
        read_only_fields = ['DeviceTokenId', 'CreatedAt']
