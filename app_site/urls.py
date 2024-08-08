from django.urls import path, re_path as url
from app_site import views
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('CURDSiteSettings/', views.CURDSiteSettingsApi),
    url(r'^CURDSiteSettingsApiCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$', views.CURDSiteSettingsApiCompanyId),

    url(r'^CURDSiteSettingsApiById/(?P<SiteSettingsId>[0-9a-zA-Z\-]+)$', views.CURDSiteSettingsApiById),

    url(r'^UploadSiteSettingsImage/(?P<SiteSettingsId>[0-9a-zA-Z\-]+)$',
        views.UploadSiteSettingsImage.as_view()),

path('GetNotificationByToUser/', views.GetNotificationByToUser.as_view()),
    
  

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)