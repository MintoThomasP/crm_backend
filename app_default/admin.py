from django.contrib import admin

from app_default.models import Currency, DepositTo, InvoiceStatus, PaymentMode, TaskStatus, UserType

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