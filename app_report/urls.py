from django.urls import path, re_path as url
from app_report import views


urlpatterns = [
    path('StaffReportApiByStaffId/', views.StaffReportApiByStaffId),
    # path('AllStaffReport/', views.AllStaffReportApi),
    path('ProjectReportApiByProjectId/', views.ProjectReportApiByProjectId),

   
    path('getAllProjectReport/', views.getAllProjectReport),

    path('StaffDailyReport/<str:CurrentDate>/<str:StaffId>/', views.StaffDailyReport),

    

    path('ReportApiBytaskId/', views.ReportApiBytaskId),

]