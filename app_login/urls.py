from django.urls import path, re_path as url
from app_login import views

urlpatterns = [

  
    path('CreateloginApi/', views.CreateLoginApi),
    path('Login/', views.loginApi),
    url(r'^Login/(?P<UserId>[0-9a-zA-Z\-]+)$', views.UserLoginApiById),
    path('UpdateUserTypeApi/', views.UpdateUserTypeApi),
    path('loginByTokenApi/', views.loginByTokenApi),



    path('LoginHistory/', views.LoginHistoryApi),
    url(r'^LoginHistoryApiById/(?P<LoginHistoryId>[0-9a-zA-Z\-]+)$', views.LoginHistoryApiById),
    url(r'^LoginHistoryApiByUserId/(?P<UserId>[0-9a-zA-Z\-]+)$', views.LoginHistoryApiByUserId),


    path('AutoLogout/', views.AutoLogout),

]
