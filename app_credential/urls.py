from django.urls import path, re_path as url
from app_credential import views


urlpatterns = [
    path('CredentialsApi/', views.CredentialsApi),
    url(r'^CredentialsApiById/(?P<CredentialId>[0-9a-zA-Z\-]+)$', views.CredentialsApiById),
    path('CredentialsPagination/', views.CredentialsPagination.as_view()),

]