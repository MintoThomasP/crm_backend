from django.urls import path, re_path as url
from app_default import views


urlpatterns = [
    path('TaskStatus/', views.TaskStatusApi),
    url(r'^TaskStatusById/(?P<StatusId>[0-9a-zA-Z\-]+)$', views.TaskStatusApiById),
    path('get_permissions/',views.get_permissions),

path('UserType/', views.UserTypeApi),



    path('Currency/', views.CurrencyApi),
    path('PaymentMode/', views.PaymentModeApi),
    path('DepositTo/', views.DepositToApi),
    path('InvoiceStatus/', views.InvoiceStatusApi),



 


   path('StaffStatusApi/', views.StaffStatusApi),
   path('LeaveTypeApi/', views.LeaveTypeApi),
   path('LeaveStatus/', views.LeaveStatusApi),
   
 

    path('DocumentTypeApi/', views.DocumentTypeApi),
    path('SectionTypeApi/', views.SectionTypeApi),
    path('CategoryTypeApi/', views.CategoryTypeApi),
    path('ReportTypeApi/', views.ReportTypeApi),
    path('MeetingTypeApi/', views.MeetingTypeApi),
    path('EnquiryTypeApi/', views.EnquiryTypeApi),
    path('FollowUpStatusApi/', views.FollowUpStatusApi),
    path('FollowUpTypeApi/', views.FollowUpTypeApi),
    path('EnquiryStatusApi/', views.EnquiryStatusApi),
    path('CountryCodeApi/', views.CountryCodeApi),


]
