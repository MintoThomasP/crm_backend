from django.urls import path, re_path as url
from app_login import views

urlpatterns = [

  
    path('CreateloginApi/', views.CreateLoginApi),
    path('Login/', views.loginApi),
    url(r'^Login/(?P<UserId>[0-9a-zA-Z\-]+)$', views.UserLoginApiById),
]
