from rest_framework import serializers
from app_accounting.models import Account, JournalEntry, JournalItem

class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = '__all__'


class JournalEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalEntry
        fields = '__all__'


class JournalItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = JournalItem
        fields = '__all__'
