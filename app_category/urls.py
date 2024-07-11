from django.urls import path, re_path as url
from app_category import views


urlpatterns = [
    path('CURDCategory/', views.CategoryApi),
    url(r'^CURDCategory/(?P<CategoryId>[0-9a-zA-Z\-]+)$', views.CategoryApiById),
    path('GetAllCategoryBySectionTypeApi/', views.GetAllCategoryBySectionTypeApi),


]