from django.urls import path, re_path as url
from app_sale import views
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Quotation/', views.QuotationApi),
    url(r'^QuotationApiById/(?P<QuotationId>[0-9a-zA-Z\-]+)$', views.QuotationApiById),
    path('QuotationApiByCompanyId/', views.QuotationApiByCompanyId.as_view()),

    path('QuotationItem/', views.QuotationItemApi),
    url(r'^QuotationItemApiById/(?P<QuotationItemId>[0-9a-zA-Z\-]+)$', views.QuotationItemApiById),
    path('UploadQuotationFile/', views.UploadQuotationFile.as_view()),
    url(r'^QuotationFileApiById/(?P<QuotationFileId>[0-9a-zA-Z\-]+)$', views.QuotationFileApiById),


    path('Invoice/', views.InvoiceApi),
    url(r'^InvoiceApiById/(?P<InvoiceId>[0-9a-zA-Z\-]+)$', views.InvoiceApiById),
  
    path('InvoiceApiByCompanyId/', views.InvoiceApiByCompanyId.as_view()),

    path('InvoiceItem/', views.InvoiceItemApi),
    url(r'^InvoiceItemApiById/(?P<InvoiceItemId>[0-9a-zA-Z\-]+)$', views.InvoiceItemApiById),
    path('UploadInvoiceDocument/', views.UploadInvoiceDocument.as_view()),
    url(r'^InvoiceDocumentApiById/(?P<InvoiceDocumentId>[0-9a-zA-Z\-]+)$', views.InvoiceDocumentApiById),

    url(r'^invoice-summary/(?P<CompanyId>[0-9a-zA-Z\-]+)$',views.invoice_summary_view),

    path('PaymentReceivedApi/', views.PaymentReceivedApi),
    url(r'^PaymentReceivedApiById/(?P<PaymentReceivedId>[0-9a-zA-Z\-]+)$', views.PaymentReceivedApiById),
    path('UploadPaymentDocument/', views.UploadPaymentDocument.as_view()),
    url(r'^PaymentDocumentApiById/(?P<PaymentDocumentId>[0-9a-zA-Z\-]+)$', views.PaymentDocumentApiById),
  
    path('PaymentReceivedApiCompanyId/', views.PaymentReceivedApiCompanyId.as_view()),

    path('PaymentReceivedDetail/', views.PaymentReceivedDetailApi),
    url(r'^PaymentReceivedDetailApiById/(?P<PaymentReceivedDetailId>[0-9a-zA-Z\-]+)$', views.PaymentReceivedDetailApiById),
    url(r'^PaymentReceivedApClientId/(?P<ClientId>[0-9a-zA-Z\-]+)$', views.PaymentReceivedApClientId),


    url(r'^DownloadPDF/(?P<InvoiceId>[0-9a-zA-Z\-]+)$', views.DownloadPDF.as_view()),
    url(r'^ViewPDF/(?P<InvoiceId>[0-9a-zA-Z\-]+)$', views.ViewPDF),
       path('SendInvoice/', views.SendInvoice),


    url(r'^GetAllUnpaidInvoiceByClientIdApi/(?P<ClientId>[0-9a-zA-Z\-]+)$', views.GetAllUnpaidInvoiceByClientIdApi),

    url(r'^ViewPDFWoodsInteriors/(?P<InvoiceId>[0-9a-zA-Z\-]+)$', views.ViewPDFWoodsInteriors),


url(r'^ViewPaymentPDF/(?P<PaymentReceivedId>[0-9a-zA-Z\-]+)$', views.ViewPaymentPDF),
url(r'^DownloadPaymentPDF/(?P<PaymentReceivedId>[0-9a-zA-Z\-]+)$', views.DownloadPaymentPDF.as_view()),

url(r'^ViewQuotationPDF/(?P<QuotationId>[0-9a-zA-Z\-]+)$', views.ViewQuotationPDF),
    ]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)