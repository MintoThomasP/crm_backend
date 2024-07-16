from django.urls import path, re_path as url
from app_default import views


urlpatterns = [
    path('TaskStatus/', views.TaskStatusApi),
    url(r'^TaskStatusById/(?P<StatusId>[0-9a-zA-Z\-]+)$', views.TaskStatusApiById),
    path('get_permissions/',views.get_permissions),

    path('Designation/', views.DesignationApi),
    url(r'^Designation/(?P<DesignationId>[0-9a-zA-Z\-]+)$',
        views.DesignationApiById),

    path('UserGroup/', views.UserGroupApi),
    url(r'^UserGroup/(?P<UserGroupId>[0-9a-zA-Z\-]+)$',
        views.UserGroupApiById),
   path('UserType/', views.UserTypeApi),



    path('Currency/', views.CurrencyApi),
    path('PaymentMode/', views.PaymentModeApi),
    path('DepositTo/', views.DepositToApi),
    path('InvoiceStatus/', views.InvoiceStatusApi),



    path('State/', views.StateApi),
    url(r'^StateApiById/(?P<StateId>[0-9a-zA-Z\-]+)$', views.StateApiById),
    url(r'^StateApiByCountryId/(?P<CountryId>[0-9a-zA-Z\-]+)$', views.StateApiByCountryId),


   path('StaffStatusApi/', views.StaffStatusApi),
   path('LeaveTypeApi/', views.LeaveTypeApi),
   path('LeaveStatus/', views.LeaveStatusApi),
   
    path('Country/', views.CountryApi),
    url(r'^CountryApiById/(?P<CountryId>[0-9a-zA-Z\-]+)$', views.CountryApiById),


    path('DocumentTypeApi/', views.DocumentTypeApi),
    path('SectionTypeApi/', views.SectionTypeApi),
    path('CategoryTypeApi/', views.CategoryTypeApi),
    path('ReportTypeApi/', views.ReportTypeApi),


]
