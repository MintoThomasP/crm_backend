from django.urls import path, re_path as url
from app_report import views


urlpatterns = [
    # path('StaffReportApiByStaffId/', views.StaffReportApiByStaffId),
    # path('AllStaffReport/', views.AllStaffReportApi),
    path('ProjectReportApiByProjectId/', views.ProjectReportApiByProjectId),
    path('ClientReportApiByClientId/', views.ClientReportApiByClientId),

   
    path('getAllProjectReport/', views.getAllProjectReport),

    path('StaffDailyReport/<str:StaffId>/', views.StaffDailyReportinPDFformat),

    path('StaffTaskReportBasedOnDateinPDFformat/<str:StaffId>/<str:StartDate>/<str:EndDate>/', views.StaffTaskReportBasedOnDateinPDFformat),

    path('StaffTaskReportBasedOnDateinPDFformat/<str:StaffId>/', views.StaffTaskReportBasedOnDateinPDFformat),


    # path('ReportApiBytaskId/', views.ReportApiBytaskId),


    path('StaffReportApiByStaffId/', views.StaffReportApiByStaffId),

    path('FinanceReport/<str:startdate>/<str:enddate>/<str:ClientId>/<ReportType>', views.FinanceReport),
    path('FinanceReportPDF/<str:startdate>/<str:enddate>/<str:ClientId>/<ReportType>/<NoOfMonths>', views.FinanceReportPDF),
    path('FinanceReportExcel/<str:startdate>/<str:enddate>/<str:ClientId>/<ReportType>/<NoOfMonths>', views.FinanceReportExcel),


    path('DownloadSummarizedStaffReportByStaffId/<str:StaffId>/', views.DownloadSummarizedStaffReportByStaffId),
        path('DownloadSummarizedStaffReportByStaffId/<str:StaffId>/<str:StartDate>/<str:EndDate>', views.DownloadSummarizedStaffReportByStaffId),

#  path('report/', views.report_view, name='report_view'),
]