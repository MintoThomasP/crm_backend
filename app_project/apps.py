from django.apps import AppConfig
from django.utils import timezone
from datetime import timedelta

class AppProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_project'

    # def ready(self):
        
    #     from django_q.tasks import schedule
    #     from django_q.models import Schedule
    #     from app_project.views import schedule_repeated_tasks

    #     schedule(
    #         'app_project.views.schedule_repeated_tasks', 
    #         schedule_type=Schedule.MINUTES, 
    #         minutes=2,  # Adjust as necessary
    #         next_run=timezone.now() + timedelta(seconds=10)
    #     )
