from django.contrib import admin
from app_accounting.models import Account, JournalEntry, JournalItem, Expense

class AccountAdmin(admin.ModelAdmin):
    list_display = ('Code', 'Name', 'Type', 'IsCashOrBank', 'CompanyId')
    list_filter = ('Type', 'IsCashOrBank', 'CompanyId')
    search_fields = ('Code', 'Name')

class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('Date', 'ReferenceNumber', 'Source', 'Narration', 'CompanyId')
    list_filter = ('Source', 'CompanyId')
    search_fields = ('ReferenceNumber', 'Narration')

class JournalItemAdmin(admin.ModelAdmin):
    list_display = ('JournalItemId', 'JournalEntryId', 'AccountId', 'Debit', 'Credit', 'ClientId')
    search_fields = ('JournalEntryId', 'AccountId')

class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('ExpenseNumber', 'Date', 'AccountId', 'PaymentAccountId', 'Amount', 'CompanyId')
    list_filter = ('CompanyId',)
    search_fields = ('ExpenseNumber', 'Narration')

admin.site.register(Account, AccountAdmin)
admin.site.register(JournalEntry, JournalEntryAdmin)
admin.site.register(JournalItem, JournalItemAdmin)
admin.site.register(Expense, ExpenseAdmin)
