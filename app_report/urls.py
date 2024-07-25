from django.urls import path, re_path as url
from app_report import views


urlpatterns = [
    # path('StaffReportApiByStaffId/', views.StaffReportApiByStaffId),
    # path('AllStaffReport/', views.AllStaffReportApi),
    path('ProjectReportApiByProjectId/', views.ProjectReportApiByProjectId),

   
    path('getAllProjectReport/', views.getAllProjectReport),

    path('StaffDailyReport/<str:StaffId>/', views.StaffDailyReportinPDFformat),

    

    # path('ReportApiBytaskId/', views.ReportApiBytaskId),


    path('StaffReportApiByStaffId/', views.StaffReportApiByStaffId),

    path('PandLReport/<str:startdate>/<str:enddate>/<str:ClientId>', views.PandLReport),
    path('BalanceSheetReport/<str:startdate>/<str:enddate>/', views.BalanceSheetReport),
#  path('report/', views.report_view, name='report_view'),
]