from django.urls import path, re_path as url
from app_staff import views
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Staff/', views.staffApi),
    url(r'^Staff/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.StaffApiById),
    url(r'^staffByStaffCode/(?P<StaffCode>[0-9a-zA-Z\-]+)$', views.staffApiByStaffCode),

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
    url(r'^leaveApplicationApiByStaffId/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.leaveApplicationApiByStaffId),

path('GetAllActiveStaffList/', views.GetAllActiveStaffListApi),


path('staffSalaryByPerformance/', views.staffSalaryByPerformanceApi),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)