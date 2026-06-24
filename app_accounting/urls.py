from django.urls import path, re_path as url
from app_accounting import views

urlpatterns = [
    path('Account/', views.AccountApi),
    url(r'^AccountApiById/(?P<AccountId>[0-9a-zA-Z\-]+)$', views.AccountApiById),
    url(r'^AccountByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.AccountByCompanyId),
    url(r'^JournalItemByAccountId/(?P<AccountId>[0-9a-zA-Z\-]+)$', views.JournalItemByAccountId),
    url(r'^CashBookByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.CashBookByCompanyId),
    path('SyncLedger/', views.SyncLedger),
]
