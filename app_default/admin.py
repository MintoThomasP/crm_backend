from django.contrib import admin

from app_default.models import City, Country, Currency, DepositTo, Designation, InvoiceStatus, PaymentMode, State, TaskStatus, UserGroup, UserType

# Register your models here.


class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ('StatusId',
'Status',
'Point',)
admin.site.register(TaskStatus, TaskStatusAdmin)


class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('UserTypeId',
'UserType')
admin.site.register(UserType, UserTypeAdmin)

class DesignationAdmin(admin.ModelAdmin):
    list_display = ('SortId',
                  'DesignationId',
                  'Designation',
                  )
admin.site.register(Designation, DesignationAdmin)


class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('SortId',
                  'UserGroupId',
                  'UserGroup',
                  'AccessTo')
admin.site.register(UserGroup, UserGroupAdmin)



class CityAdmin(admin.ModelAdmin):
    list_display = ('SortId',
                  'CityId',
                  'StateId',
                  'City',
                  )
admin.site.register(City, CityAdmin)


class CountryAdmin(admin.ModelAdmin):
    list_display =('SortId',
                  'CountryId',
                  'Country',
                  )
admin.site.register(Country, CountryAdmin)


class StateAdmin(admin.ModelAdmin):
    list_display =('SortId',
                  'StateId',
                  'CountryId',
                  'State'
                  )
admin.site.register(State, StateAdmin)


class CurrencyAdmin(admin.ModelAdmin):
    list_display =('SortId',
                  'CurrencyId',
                  'Currency',  
                  )
admin.site.register(Currency, CurrencyAdmin)


class PaymentModeAdmin(admin.ModelAdmin):
    list_display =('SortId',
                  'PaymentModeId',
                  'PaymentMode',  
                  )
admin.site.register(PaymentMode, PaymentModeAdmin)


class DepositToAdmin(admin.ModelAdmin):
    list_display =('SortId',
                  'DepositToId',
                  'DepositTo',  
                  )
admin.site.register(DepositTo, DepositToAdmin)


class InvoiceStatusAdmin(admin.ModelAdmin):
    list_display =('SortId',
                  'InvoiceStatusId',
                  'InvoiceStatus',  
                  )
admin.site.register(InvoiceStatus, InvoiceStatusAdmin)