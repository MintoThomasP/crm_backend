from django.contrib import admin

from app_staff.models import Staff

# Register your models here.


class StaffAdmin(admin.ModelAdmin):
    list_display = ('SortId',
'StaffId',
'StaffName',
'PhoneNumber',
'Gender',
'DOB',
'EmailId',
'Address',
'JoinedOn')
admin.site.register(Staff, StaffAdmin)