from django.urls import path, re_path as url
from app_accounting import views

urlpatterns = [
    path('Account/', views.AccountApi),
    url(r'^AccountApiById/(?P<AccountId>[0-9a-zA-Z\-]+)$', views.AccountApiById),
    url(r'^AccountByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.AccountByCompanyId),
    url(r'^JournalItemByAccountId/(?P<AccountId>[0-9a-zA-Z\-]+)$', views.JournalItemByAccountId),
    url(r'^CashBookByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.CashBookByCompanyId),
    path('SyncLedger/', views.SyncLedger),
    url(r'^NextExpenseNumber/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.NextExpenseNumber),
    path('Expense/', views.ExpenseApi),
    url(r'^ExpenseApiById/(?P<ExpenseId>[0-9a-zA-Z\-]+)$', views.ExpenseApiById),
    url(r'^ExpenseByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.ExpenseByCompanyId),
    path('JournalEntry/', views.JournalEntryApi),
    url(r'^JournalEntryApiById/(?P<JournalEntryId>[0-9a-zA-Z\-]+)$', views.JournalEntryApiById),
]
