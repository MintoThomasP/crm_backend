from django.contrib import admin

from app_staff.models import Staff, StaffGuardian

# Register your models here.


class StaffAdmin(admin.ModelAdmin):
    list_display = ('SortId',
'StaffId',
'StaffName',
'StaffCode',
'PhoneNumber',
'Gender',
'DOB',
'EmailId',
'PermanentAddress',
'JoinedOn',
'QrCode',
'Salary',
'Designation',
'UserGroup',
'CurrentAddress')
admin.site.register(Staff, StaffAdmin)


class StaffGuardianAdmin(admin.ModelAdmin):
    list_display = ('SortId',
'StaffGuardianId',
'StaffId',
'GuardianName',
'PhoneNumber',
'EmailId',
'Relation',)
admin.site.register(StaffGuardian, StaffGuardianAdmin)