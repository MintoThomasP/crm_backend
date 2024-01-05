from django.urls import path, re_path as url
from app_login import views

urlpatterns = [

  
    path('CreateloginApi/', views.CreateLoginApi),
    path('login/', views.loginApi),
]
