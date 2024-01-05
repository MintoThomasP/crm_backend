from django.urls import path, re_path as url
from app_staff import views


urlpatterns = [
    path('Staff/', views.staffApi),
    url(r'^Staff/(?P<StaffId>[0-9a-zA-Z\-]+)$', views.StaffApiById),

   
]
