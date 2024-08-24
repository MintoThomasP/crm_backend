from django.urls import path, re_path as url
from app_website_email import views

urlpatterns = [
    
    path('mailforwebsite/', views.mailforwebsite),
]