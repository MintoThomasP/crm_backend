
from django.urls import path, re_path as url
from app_company import views

urlpatterns = [
    path('CompanyApi/', views.CompanyApi),
    url(r'^CompanyApiById/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.CompanyApiById),
    url(r'^CompanyPerformanceById/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.CompanyPerformanceById),

    path('CompanyDocumentsApi/', views.CompanyDocumentsApi),
    url(r'^CompanyDocumentsApiById/(?P<CompanyDocumentId>[0-9a-zA-Z\-]+)$', views.CompanyDocumentsApiById),


    url(r'^UploadCompanyDocuments/(?P<CompanyDocumentId>[0-9a-zA-Z\-]+)$',
        views.UploadCompanyDocuments.as_view()),


    url(r'^DeleteCompanyDataByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.DeleteCompanyDataByCompanyId),
     
]