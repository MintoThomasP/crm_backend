
from django.urls import path, re_path as url
from app_todo import views


urlpatterns = [
    path('Todo/', views.TodoApi),
    url(r'^TodoApiById/(?P<TodoId>[0-9a-zA-Z\-]+)$', views.TodoApiById),
        path('TodoPagination/', views.TodoPagination.as_view()), 
]
