from django.urls import path, re_path as url
from app_site import views
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('CURDSiteSettings/', views.CURDSiteSettingsApi),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)