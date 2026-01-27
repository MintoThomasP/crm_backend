from django.urls import path
from .views import send_contact_email

urlpatterns = [
    # Update This to match your desired API path
    path('minto-send-email/', send_contact_email, name='send_contact_email'),
]
