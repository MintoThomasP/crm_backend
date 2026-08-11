from django.urls import path
from . import views

urlpatterns = [
    path('login', views.ClientLoginView.as_view()),
    path('projects', views.ClientProjectListView.as_view()),
    path('projects/<str:project_id>', views.ClientProjectDetailView.as_view()),
    path('projects/<str:project_id>/documents', views.ProjectDocumentUploadView.as_view()),
    path('tickets', views.ClientTicketCreateView.as_view()),
]
