from rest_framework import serializers

from app_login.models import Login

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = ('SortId',
                  'LoginId',
                  'UserId',
                  'UserType',
                  'EmailId',
                  'Password',
                  'Token',
                  'Status')
        

class LoginSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = (
            'LoginId',
            'UserId',
            'UserType',
            'EmailId',
            'Password',
            'Status')
        
class LoginAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = (
            'SortId',
            'LoginId',
            'UserId',
            'UserType',
            'EmailId',
            'Token',
            'Status')
        
class LoginUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = (
            # 'SortId',
            'LoginId',
            'UserId',
            'UserType',
            'EmailId',
            'Password',)