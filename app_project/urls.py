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
    url(r'^UploadProjectTaskFile/(?P<ProjectTaskFileId>[0-9a-zA-Z\-]+)$',
        views.UploadProjectTaskFile.as_view()),



    path('Comment/', views.CommentApi),
    url(r'^CURDCommentApiById/(?P<CommentId>[0-9a-zA-Z\-]+)$', views.CURDCommentApiById),


    path('CommentFile/', views.CommentFileApi),
    url(r'^CURDCommentFileApiById/(?P<CommentFileId>[0-9a-zA-Z\-]+)$', views.CURDCommentFileApiById),
    path('UploadCommentFile/', views.UploadCommentFile.as_view()),
    path('ProjectTaskApiFilteringforTaskAssignedTo/', views.ProjectTaskApiFilteringforTaskAssignedTo), #my task
    path('ProjectTaskApiFilteringforTaskAssignedBy/', views.ProjectTaskApiFilteringforTaskAssignedBy), #task assigned by me
    path('GetAllProjectTaskApiByFiltering/', views.GetAllProjectTaskApiByFiltering), #Get all task filtering

    #  url(r'^send_notification/(?P<ProjectTaskId>[0-9a-zA-Z\-]+)$', views.send_notification_on_comment),
 path('schedule_repeated_tasks/', views.schedule_repeated_tasks),
  path('send_notification/', views.send_notification),


]
