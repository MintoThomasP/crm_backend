from django.urls import path, re_path as url
from app_vendor import views


urlpatterns = [
    path('Vendor/', views.VendorApi),
    url(r'^VendorById/(?P<VendorId>[0-9a-zA-Z\-]+)$', views.VendorApiById),
    path('VendorApiByCompanyId/', views.VendorApiByCompanyId.as_view()),
    url(r'^VendorByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.VendorByCompanyId),
   

    path('UploadVendorDocument/', views.UploadVendorDocument.as_view()),
    url(r'^VendorDocumentApiById/(?P<VendorDocumentId>[0-9a-zA-Z\-]+)$', views.VendorDocumentApiById),


    path('VendorAddress/', views.VendorAddressApi),
    url(r'^VendorAddressApiById/(?P<VendorAddressId>[0-9a-zA-Z\-]+)$', views.VendorAddressApiById),
    url(r'^VendorAddressApiByVendorId/(?P<VendorId>[0-9a-zA-Z\-]+)$', views.VendorAddressApiByVendorId),

    

    path('ContactPerson/', views.ContactPersonApi),
    url(r'^ContactPersonApiById/(?P<ContactPersonId>[0-9a-zA-Z\-]+)$', views.ContactPersonApiById),
   


    path('VendorBankDetailsApi/', views.VendorBankDetailsApi),
    url(r'^VendorBankDetailsApiById/(?P<BankDetailId>[0-9a-zA-Z\-]+)$', views.VendorBankDetailsApiById),
    url(r'^VendorBankDetailsApiByVendorId/(?P<VendorId>[0-9a-zA-Z\-]+)$', views.VendorBankDetailsApiByVendorId),
]
