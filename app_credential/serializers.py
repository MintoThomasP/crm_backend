from rest_framework import serializers

from app_credential.models import Credentials


class CredentialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Credentials
        fields = (
'SortId',
'CredentialId',
'CompanyId',
'Name',
'LoginURL',
'UserName',
'Password',
'AccessTo',
'ClientId',
'UserId')
        