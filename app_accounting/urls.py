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
    url(r'^ExportCashBook/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.ExportCashBook),
    
    path('ExpenseClaim/', views.ExpenseClaimApi),
    url(r'^ExpenseClaimApiById/(?P<ExpenseClaimId>[0-9a-zA-Z\-]+)$', views.ExpenseClaimApiById),
    url(r'^ExpenseClaimByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.ExpenseClaimByCompanyId),
    url(r'^ExpenseClaimReimburse/(?P<ExpenseClaimId>[0-9a-zA-Z\-]+)$', views.ExpenseClaimReimburse),
    url(r'^ExpenseClaimUploadReceipt/(?P<ExpenseClaimId>[0-9a-zA-Z\-]+)$', views.ExpenseClaimUploadReceipt),

    url(r'^NextLoanNumber/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.NextLoanNumber),
    url(r'^NextRepaymentNumber/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.NextRepaymentNumber),
    path('EmployeeLoan/', views.EmployeeLoanApi),
    url(r'^EmployeeLoanApiById/(?P<EmployeeLoanId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanApiById),
    url(r'^EmployeeLoanByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanByCompanyId),
    url(r'^EmployeeLoanByStaffId/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanByStaffId),
    url(r'^EmployeeLoanUploadReceipt/(?P<EmployeeLoanId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanUploadReceipt),

    path('EmployeeLoanRepayment/', views.EmployeeLoanRepaymentApi),
    url(r'^EmployeeLoanRepaymentApiById/(?P<RepaymentId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanRepaymentApiById),
    url(r'^EmployeeLoanRepaymentsByLoanId/(?P<EmployeeLoanId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanRepaymentsByLoanId),
    url(r'^EmployeeLoanRepaymentUploadReceipt/(?P<RepaymentId>[0-9a-zA-Z\-]+)$', views.EmployeeLoanRepaymentUploadReceipt),
]

