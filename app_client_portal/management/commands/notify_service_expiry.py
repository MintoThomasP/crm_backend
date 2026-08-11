import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from app_project.models import ProjectService, Project
from app_client.models import Client
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Checks ProjectService expiry dates and sends notifications to clients.'

    def handle(self, *args, **kwargs):
        today = datetime.now().date()
        notification_days = [30, 15, 7, 3, 1]
        
        services = ProjectService.objects.filter(IsActive=True, NotifyClient=True, ExpiryDate__isnull=False)
        
        for service in services:
            if not service.ExpiryDate:
                continue
            
            expiry_date = service.ExpiryDate.date() if isinstance(service.ExpiryDate, datetime) else service.ExpiryDate
            days_until_expiry = (expiry_date - today).days
            
            if days_until_expiry in notification_days or days_until_expiry == 0:
                self.send_notification(service, days_until_expiry)
                
    def send_notification(self, service, days_left):
        try:
            project = Project.objects.get(ProjectId=service.ProjectId)
            client = Client.objects.get(ClientId=project.ClientId)
            
            subject = f"Service Expiry Notification: {service.ServiceName}"
            
            if days_left == 0:
                message = f"Dear {client.FirstName},\n\nYour service '{service.ServiceName}' for project '{project.ProjectName}' expires TODAY. Please renew it immediately to avoid disruption."
            else:
                message = f"Dear {client.FirstName},\n\nYour service '{service.ServiceName}' for project '{project.ProjectName}' will expire in {days_left} days (on {service.ExpiryDate.strftime('%Y-%m-%d')}).\nPlease arrange for renewal.\n\nThank you."
            
            # Use Django's configured email backend
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [client.EmailId],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully sent notification to {client.EmailId} for {service.ServiceName}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error sending notification for service {service.ProjectServiceId}: {str(e)}'))
