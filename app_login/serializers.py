from rest_framework import serializers

from app_login.models import Login, LoginHistory

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
class SaveTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Login
        fields = (
                  'LoginId',
                  'UserId',
                  'Token')
        

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
        


class LoginHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginHistory
        fields = ('SortId',
                  'LoginHistoryId',
                  'LoginId',
                  'UserId',
                  'LoginTime',
                  'LogoutTime')