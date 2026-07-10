from django.urls import path, re_path as url
from app_client import views


urlpatterns = [
    path('Client/', views.clientApi),
    url(r'^ClientById/(?P<ClientId>[0-9a-zA-Z\-]+)$', views.ClientApiById),
    path('ClientApiByCompanyId/', views.ClientApiByCompanyId.as_view()),
    url(r'^ClientByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.ClientByCompanyId),
    url(r'^getAllClientReport/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.clientApi),
    path('getClientReport/', views.getClientReport.as_view()),

    path('ClientOtherDetails/', views.ClientOtherDetailsApi),
    url(r'^ClientOtherDetailsApiById/(?P<ClientOtherDetailId>[0-9a-zA-Z\-]+)$',
        views.ClientOtherDetailsApiById),


    path('ClientDocument/', views.ClientDocument),
    path('UploadClientDocument/', views.UploadClientDocument.as_view()),
    url(r'^ClientDocumentApiById/(?P<ClientDocumentId>[0-9a-zA-Z\-]+)$',
        views.ClientDocumentApiById),


    path('ClientAddress/', views.ClientAddressApi),
    url(r'^ClientAddressApiById/(?P<ClientAddressId>[0-9a-zA-Z\-]+)$',
        views.ClientAddressApiById),
    url(r'^ClientAddressApiByClientId/(?P<ClientId>[0-9a-zA-Z\-]+)$',
        views.ClientAddressApiByClientId),


    path('ContactPerson/', views.ContactPersonApi),
    url(r'^ContactPersonApiById/(?P<ContactPersonId>[0-9a-zA-Z\-]+)$',
        views.ContactPersonApiById),

    path('ClientReminder/', views.ClientReminderApi),
    url(r'^ClientReminderApiById/(?P<ClientReminderId>[0-9a-zA-Z\-]+)$',
        views.ClientReminderApiById),

    path('ClientVisitRegister/', views.ClientVisitRegisterApi),
    url(r'^ClientVisitRegisterByClientId/(?P<ClientId>[0-9a-zA-Z\-]+)$',
        views.ClientVisitRegisterApi),
    url(r'^ClientVisitRegister/(?P<ClientVisitRegisterId>[0-9a-zA-Z\-]+)$',
        views.ClientVisitRegisterApiById),



    path('ClientBankDetailsApi/', views.ClientBankDetailsApi),
    url(r'^ClientBankDetailsApiById/(?P<BankDetailId>[0-9a-zA-Z\-]+)$',
        views.ClientBankDetailsApiById),
    url(r'^ClientBankDetailsApiByClientId/(?P<ClientId>[0-9a-zA-Z\-]+)$',
        views.ClientBankDetailsApiByClientId),

    url(r'^Opportunity/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.OpportunityApi),
    url(r'^OpportunityApiById/(?P<OpportunityId>[0-9a-zA-Z\-]+)$', views.OpportunityApiById),
    url(r'^SupportTicket/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.SupportTicketApi),
    url(r'^SupportTicketApiById/(?P<TicketId>[0-9a-zA-Z\-]+)$', views.SupportTicketApiById),
    
    url(r'^ContactGroup/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.ContactGroupApi),
    url(r'^ContactGroupApiById/(?P<GroupId>[0-9a-zA-Z\-]+)$', views.ContactGroupApiById),
    url(r'^InteractionLog/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.InteractionLogApi),
    url(r'^InteractionLogByClientId/(?P<ClientId>[0-9a-zA-Z\-]+)$', views.InteractionLogApiByClientId),
]
