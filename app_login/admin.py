from django.contrib import admin

from app_login.models import Login

# Register your models here.


class LoginAdmin(admin.ModelAdmin):
    list_display = ('SortId',
                  'LoginId',
                  'UserId',
                  'UserType',
                  'EmailId',
                  'Password',
                  'Token',
                  'Status')
admin.site.register(Login, LoginAdmin)