from django.urls import path, re_path as url
from app_category import views


urlpatterns = [
    path('CURDCategory/', views.CategoryApi),
    url(r'^CURDCategory/(?P<CategoryId>[0-9a-zA-Z\-]+)$', views.CategoryApiById),
    path('GetAllCategoryBySectionTypeApi/', views.GetAllCategoryBySectionTypeApi),


    path('CURDReport/', views.ReportApi),
    url(r'^ReportApiById/(?P<ReportId>[0-9a-zA-Z\-]+)$', views.ReportApiById),

    path('SaveReportRefFile/', views.SaveReportRefFile.as_view()),

    path('GetAllCategoryandSubCategories/', views.GetAllCategoryandSubCategories),
    path('GetCategoryandSubCategoriesByCategoryType/', views.GetCategoryandSubCategoriesByCategoryType),
    path('GetClientReportMonthly/', views.GetClientReportMonthly),
    path('GetAllLedgerCategory/', views.GetAllLedgerCategory),

    path('SaveReport/', views.BulkCreateReportView.as_view()),

    url(r'^DeleteReportRefFileById/(?P<ReportRefFileId>[0-9a-zA-Z\-]+)$', views.DeleteReportRefFileById),

]