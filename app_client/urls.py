from django.urls import path, re_path as url
from app_client import views


urlpatterns = [
    path('Client/', views.clientApi),
    url(r'^ClientById/(?P<ClientId>[0-9a-zA-Z\-]+)$', views.ClientApiById),

    path('ClientOtherDetails/', views.ClientOtherDetailsApi),
    url(r'^ClientOtherDetailsApiById/(?P<ClientOtherDetailId>[0-9a-zA-Z\-]+)$', views.ClientOtherDetailsApiById),

    path('UploadClientDocument/', views.UploadClientDocument.as_view()),


    path('ClientAddress/', views.ClientAddressApi),
    url(r'^ClientAddressApiById/(?P<ClientAddressId>[0-9a-zA-Z\-]+)$', views.ClientAddressApiById),
    url(r'^ClientAddressApiByClientId/(?P<ClientId>[0-9a-zA-Z\-]+)$', views.ClientAddressApiByClientId),

    

    path('ContactPerson/', views.ContactPersonApi),
    url(r'^ContactPersonApiById/(?P<ContactPersonId>[0-9a-zA-Z\-]+)$', views.ContactPersonApiById),

   
]
