from django.urls import path, re_path as url
from app_project import views


urlpatterns = [
    path('Project/', views.ProjectApi),
    url(r'^ProjectById/(?P<ProjectId>[0-9a-zA-Z\-]+)$', views.ProjectApiById),
    path('ProjectApiByCompanyId/', views.ProjectApiByCompanyId.as_view()),
    url(r'^ProjectByCompanyId/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.ProjectByCompanyId),
    url(r'^getAllProjectReport/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.ProjectApi),

    path('ProjectTask/', views.ProjectTaskApi),
    # currently using this API for get all Task, my Task, task assigned by me
    path('ProjectTaskPagination/', views.ProjectTaskPagination.as_view()),

    url(r'^ProjectTaskById/(?P<ProjectTaskId>[0-9a-zA-Z\-]+)$',
        views.ProjectTaskApiById),
    url(r'^ProjectTaskApiByProjectId/(?P<ProjectId>[0-9a-zA-Z\-]+)$',
        views.ProjectTaskApiByProjectId),
    url(r'^ProjectTaskApiByUserId/(?P<TaskAssignedTo>[0-9a-zA-Z\-]+)$',
        views.ProjectTaskApiByUserId),
    url(r'^ProjectTaskApiByTaskAssignedBy/(?P<TaskAssignedBy>[0-9a-zA-Z\-]+)$',
        views.ProjectTaskApiByTaskAssignedBy),
    path('ProjectTaskApiByUserIdAndProjectId/',
         views.ProjectTaskApiByUserIdAndProjectId),
    path('ProjectTaskApiByTaskAssignedByAndProjectId/',
         views.ProjectTaskApiByTaskAssignedByAndProjectId),



    path('TaskReviews/', views.TaskReviewsApi),
    url(r'^TaskReviewsById/(?P<TaskReviewId>[0-9a-zA-Z\-]+)$',
        views.TaskReviewsApiById),
    path('GetAllTasksStatus/', views.GetAllTasksStatus),



    path('ProjectTaskFile/', views.ProjectTaskFileApi),
    url(r'^ProjectTaskFile/(?P<ProjectTaskFileId>[0-9a-zA-Z\-]+)$',
        views.CURDprojectTaskFileApiById),
    url(r'^UploadProjectTaskFile/(?P<ProjectTaskFileId>[0-9a-zA-Z\-]+)$',
        views.UploadProjectTaskFile.as_view()),



    path('Comment/', views.CommentApi),
    url(r'^CURDCommentApiById/(?P<CommentId>[0-9a-zA-Z\-]+)$',
        views.CURDCommentApiById),


    path('CommentFile/', views.CommentFileApi),
    url(r'^CURDCommentFileApiById/(?P<CommentFileId>[0-9a-zA-Z\-]+)$',
        views.CURDCommentFileApiById),
    path('UploadCommentFile/', views.UploadCommentFile.as_view()),
    path('ProjectTaskApiFilteringforTaskAssignedTo/',
         views.ProjectTaskApiFilteringforTaskAssignedTo),  # my task
    path('ProjectTaskApiFilteringforTaskAssignedBy/',
         views.ProjectTaskApiFilteringforTaskAssignedBy),  # task assigned by me
    path('GetAllProjectTaskApiByFiltering/',
         views.GetAllProjectTaskApiByFiltering),  # Get all task filtering

    path('schedule_repeated_tasks/', views.schedule_repeated_tasks),

    path('ProjectTaskTimingApi/', views.ProjectTaskTimingApi),
    url(r'^CURDprojectTaskTimingApiById/(?P<ProjectTaskTimingId>[0-9a-zA-Z\-]+)$',
        views.CURDprojectTaskTimingApiById),
    url(r'^ProjectTaskTimingApiByProjectTaskId/(?P<ProjectTaskId>[0-9a-zA-Z\-]+)$',
        views.ProjectTaskTimingApiByProjectTaskId),
    url(r'^getLastTimmingByTaskId/(?P<ProjectTaskId>[0-9a-zA-Z\-]+)$',
        views.getLastTimmingByTaskId),
    url(r'^ProjectTaskTimingCalculationById/(?P<ProjectTaskTimingId>[0-9a-zA-Z\-]+)$',
        views.ProjectTaskTimingCalculationById),


    # path('ProjectTaskTotalDurationCalculation/', views.ProjectTaskTotalDurationCalculation),
    # only using this API for get all tickets, and tickets assigned by me and filteration
    path('GetAllTicketsApi/', views.GetAllTicketsApi.as_view()),

    url(r'^TicketsByTaskAssignedTo/(?P<TaskAssignedTo>[0-9a-zA-Z\-]+)$',
        views.TicketsByTaskAssignedTo),
    url(r'^TicketsByTaskAssignedBy/(?P<TaskAssignedBy>[0-9a-zA-Z\-]+)$',
        views.TicketsByTaskAssignedBy),


    path('RestTaskPoint/', views.RestTaskPoint),
    url(r'^GetallTaskTemplate/(?P<CompanyId>[0-9a-zA-Z\-]+)$',
        views.GetallTaskTemplate),

    path('GetAllTemplatesByPagination/',
         views.GetAllTemplatesByPagination.as_view()),

    url(r'^copy_image/(?P<ProjectTaskFileId>[0-9a-zA-Z\-]+)$',
        views.copy_image),

    path('savecopy_image/', views.savecopy_image),
    path('UpdateClientandCompanyInTask/', views.UpdateClientandCompanyInTask),
    path('ProjectTaskTimingCalculation/', views.ProjectTaskTimingCalculation),
    path('ProjectTaskendatedurationCalculation/',
         views.ProjectTaskendatedurationCalculation),
    path('DeleteTaskByAdmin/', views.DeleteTaskByAdmin),

]
