from django.urls import path, re_path as url
from app_staff import views
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Staff/', views.staffApi),
    url(r'^Staff/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.StaffApiById),
    url(r'^DashboardData/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.DashboardData),
    url(r'^GetSalarySlipByStaffId/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.GetSalarySlipByStaffId),
    url(r'^staffByStaffCode/(?P<StaffCode>[0-9a-zA-Z\-]+)$', views.staffApiByStaffCode),
    path('StaffApiByCompanyId/', views.StaffApiByCompanyId.as_view()), # pagination for staff manage table
       url(r'^StaffPerformanceByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.StaffPerformanceByCompanyId),
       url(r'^getAllStaffReport/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.staffApi),


    path('StaffGuardian/', views.staffGuardianApi),
    url(r'^StaffGuardian/(?P<StaffGuardianId>[0-9a-zA-Z\-]+)$', views.staffGuardianApiById),
    url(r'^StaffGuardianByStaffId/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.staffGuardianApiByStaffId),

   url(r'^uploadStaffProfileImage/(?P<pk>[0-9a-zA-Z\-]+)$',
        views.uploadStaffProfileImage.as_view()),


    path('staffDocumentsApi/', views.staffDocumentsApi),
    url(r'^staffDocumentsApiById/(?P<StaffDocumentId>[0-9a-zA-Z\-]+)$', views.staffDocumentsApiById),
   url(r'^uploadStaffDocuments/(?P<StaffDocumentId>[0-9a-zA-Z\-]+)$',
        views.uploadStaffDocuments.as_view()),
        url(r'^staffDocumentsApiByStaffId/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.staffDocumentsApiByStaffId),


    path('leaveApplicationApi/', views.leaveApplicationApi),
    url(r'^leaveApplicationApiById/(?P<LeaveApplicationId>[0-9a-zA-Z\-]+)$', views.leaveApplicationApiById),
    path('GetAllLeaveApplicationByCompanyId/', views.GetAllLeaveApplicationByCompanyId.as_view()), # pagination for leave application for admin side
    path('leaveApplicationApiByStaffId/', views.leaveApplicationApiByStaffId.as_view()), #  pagination for leave application for staff login

# path('GetAllActiveStaffList/', views.GetAllActiveStaffListApi),
url(r'^GetAllActiveStaffList/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.GetAllActiveStaffListApi),


path('staffSalaryByPerformance/', views.staffSalaryByPerformanceApi),
path('CreateSalarySlip/<str:CompanyId>/', views.CreateSalarySlipApi),
    # url(r'^CreateSalarySlip/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.CreateSalarySlipApi),
    path('DownloadSalarySlip/<str:Month>/<str:Year>/<str:StaffId>', views.DownloadSalarySlip),

path('CURDSalarySlipApi/', views.CURDSalarySlipApi),


    path('moveOnRegister/', views.moveOnRegisterApi),
    url(r'^moveOnRegister/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.moveOnRegisterApi),
    path('StaffPerformanceByCompanyId/<str:CompanyId>/', views.StaffPerformanceByCompanyId),



    path('StaffBankDetailsApi/', views.StaffBankDetailsApi),
    url(r'^staffBankDetailsApiById/(?P<BankDetailId>[0-9a-zA-Z\-]+)$', views.staffBankDetailsApiById),
    url(r'^staffBankDetailsApiByStaffId/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.staffBankDetailsApiByStaffId),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)