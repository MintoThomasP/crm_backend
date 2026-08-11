from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'documents', views.ClientDocumentUploadViewSet)
router.register(r'alerts', views.ServiceExpiryAlertViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('generate-access/', views.generate_portal_access, name='generate_portal_access'),
    path('login/', views.client_portal_login, name='client_portal_login'),
    path('dashboard-stats/<str:client_id>/', views.client_dashboard_stats, name='client_dashboard_stats'),
    path('projects/<str:client_id>/', views.client_projects, name='client_projects'),
    path('tickets/<str:client_id>/', views.client_tickets, name='client_tickets'),
]
