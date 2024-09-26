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




    path('Unit/', views.UnitApi),
    url(r'^UnitApiById/(?P<UnitId>[0-9a-zA-Z\-]+)$',
        views.UnitApiById),
    url(r'^UnitByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.UnitByCompanyId),

    path('WorkPlaceApi/', views.WorkPlaceApi),
    url(r'^WorkPlaceApiById/(?P<WorkPlaceId>[0-9a-zA-Z\-]+)$',
        views.WorkPlaceApiById),
    url(r'^WorkPlaceByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.WorkPlaceByCompanyId),


    path('ProjectScopeApi/', views.ProjectScopeApi),
    url(r'^ProjectScopeApiById/(?P<ProjectScopeId>[0-9a-zA-Z\-]+)$',
        views.ProjectScopeApiById),
    url(r'^ProjectScopeByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.ProjectScopeByCompanyId),



    path('BusinessCategoryApi/', views.BusinessCategoryApi),
    url(r'^BusinessCategoryApiById/(?P<BusinessCategoryId>[0-9a-zA-Z\-]+)$',
        views.BusinessCategoryApiById),
    url(r'^BusinessCategoryByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.BusinessCategoryByCompanyId),

  path('ElementCategoryApi/', views.ElementCategoryApi),
    url(r'^ElementCategoryApiById/(?P<ElementCategoryId>[0-9a-zA-Z\-]+)$',
        views.ElementCategoryApiById),
    url(r'^ElementCategoryByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.ElementCategoryByCompanyId),
]