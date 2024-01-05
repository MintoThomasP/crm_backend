from django.urls import path, re_path as url
from app_default import views


urlpatterns = [
    path('TaskStatus/', views.TaskStatusApi),
    url(r'^TaskStatusById/(?P<StatusId>[0-9a-zA-Z\-]+)$', views.TaskStatusApiById),

   
   
]
