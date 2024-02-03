from django.urls import path, re_path as url
from app_project import views


urlpatterns = [
    path('Project/', views.ProjectApi),
    url(r'^ProjectById/(?P<ProjectId>[0-9a-zA-Z\-]+)$', views.ProjectApiById),

    path('ProjectTask/', views.ProjectTaskApi),
    url(r'^ProjectTaskById/(?P<ProjectTaskId>[0-9a-zA-Z\-]+)$', views.ProjectTaskApiById),
    url(r'^ProjectTaskApiByProjectId/(?P<ProjectId>[0-9a-zA-Z\-]+)$', views.ProjectTaskApiByProjectId),
    url(r'^ProjectTaskApiByUserId/(?P<TaskAssignedTo>[0-9a-zA-Z\-]+)$', views.ProjectTaskApiByUserId),
    url(r'^ProjectTaskApiByTaskAssignedBy/(?P<TaskAssignedBy>[0-9a-zA-Z\-]+)$', views.ProjectTaskApiByTaskAssignedBy),
    path('ProjectTaskApiByUserIdAndProjectId/', views.ProjectTaskApiByUserIdAndProjectId),
    path('ProjectTaskApiByTaskAssignedByAndProjectId/', views.ProjectTaskApiByTaskAssignedByAndProjectId),



    path('TaskReviews/', views.TaskReviewsApi),
    url(r'^TaskReviewsById/(?P<TaskReviewId>[0-9a-zA-Z\-]+)$', views.TaskReviewsApiById),
    path('GetAllTasksStatus/', views.GetAllTasksStatus),



    path('ProjectTaskFile/', views.ProjectTaskFileApi),
    url(r'^ProjectTaskFile/(?P<ProjectTaskFileId>[0-9a-zA-Z\-]+)$', views.CURDprojectTaskFileApiById),
    url(r'^uploadProjectTaskFile/(?P<ProjectTaskFileId>[0-9a-zA-Z\-]+)$',
        views.UploadProjectTaskFile.as_view()),

]
