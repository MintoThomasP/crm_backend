from django.urls import path, re_path as url
from app_basic import views


urlpatterns = [
    path('Designation/', views.DesignationApi),
    url(r'^Designation/(?P<DesignationId>[0-9a-zA-Z\-]+)$',
        views.DesignationApiById),
    url(r'^DesignationByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.DesignationByCompanyId),

    path('UserGroup/', views.UserGroupApi),
    url(r'^UserGroup/(?P<UserGroupId>[0-9a-zA-Z\-]+)$',
        views.UserGroupApiById),
    url(r'^UserGroupByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.UserGroupByCompanyId),

    path('State/', views.StateApi),
    url(r'^StateApiById/(?P<StateId>[0-9a-zA-Z\-]+)$', views.StateApiById),
    url(r'^StateApiByCountryId/(?P<CountryId>[0-9a-zA-Z\-]+)$', views.StateApiByCountryId),

    path('Country/', views.CountryApi),
    url(r'^CountryApiById/(?P<CountryId>[0-9a-zA-Z\-]+)$', views.CountryApiById),

    path('UserPermissionApi/', views.UserPermissionApi),
    path('UserPermissionbySectionType/', views.UserPermissionbySectionTypeApi),
    
    path('TempleteType/', views.TempleteTypeApi),
    url(r'^TempleteType/(?P<TempleteTypeId>[0-9a-zA-Z\-]+)$',
        views.TempleteTypeApiById),
    url(r'^TempleteTypeByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.TempleteTypeByCompanyId),
]