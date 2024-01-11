from django.urls import path, re_path as url
from app_staff import views
from django.conf import settings
from django.conf.urls.static import static


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('Staff/', views.staffApi),
    url(r'^Staff/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.StaffApiById),

   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)