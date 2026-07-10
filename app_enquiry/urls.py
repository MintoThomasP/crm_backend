from django.urls import path, re_path as url
from app_enquiry import views

urlpatterns = [
path('EnquiryApi/', views.EnquiryApi),
url(r'^EnquiryApiById/(?P<EnquiryId>[0-9a-zA-Z\-]+)$', views.EnquiryApiById),
path('EnquiryApiByCompanyId/', views.EnquiryApiByCompanyId.as_view()),


path('CURDFollowUpApi/', views.CURDFollowUpApi),
url(r'^CURDFollowUpApiById/(?P<FollowUpId>[0-9a-zA-Z\-]+)$', views.CURDFollowUpApiById),
url(r'^CURDFollowUpApiByEnquiryId/(?P<EnquiryId>[0-9a-zA-Z\-]+)$', views.CURDFollowUpApiByEnquiryId),
# url(r'^EnquiryByScheduledTo/(?P<ScheduledTo>[0-9a-zA-Z\-]+)$', views.EnquiryByScheduledTo),

path('EnquiryByScheduledTo/', views.EnquiryByScheduledTo.as_view()),
path('leads/webhook/', views.lead_webhook_api),
url(r'^convert_lead_to_opportunity/(?P<EnquiryId>[0-9a-zA-Z\-]+)$', views.convert_lead_to_opportunity_api),
]