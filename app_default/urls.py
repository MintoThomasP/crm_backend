from django.urls import path, re_path as url
from app_default import views


urlpatterns = [
    path('TaskStatus/', views.TaskStatusApi),
    url(r'^TaskStatusById/(?P<StatusId>[0-9a-zA-Z\-]+)$', views.TaskStatusApiById),
    path('get_permissions/',views.get_permissions),

    path('Designation/', views.DesignationApi),
    url(r'^Designation/(?P<DesignationId>[0-9a-zA-Z\-]+)$',
        views.DesignationApiById),

    path('UserGroup/', views.UserGroupApi),
    url(r'^UserGroup/(?P<UserGroupId>[0-9a-zA-Z\-]+)$',
        views.UserGroupApiById),
   
   
]
