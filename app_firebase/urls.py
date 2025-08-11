from django.urls import path
from .views import DeviceTokenCreateView, SendNotificationToUserView, SendNotificationToTokenView

urlpatterns = [
    path('device-tokens/', DeviceTokenCreateView.as_view(), name='device-tokens'),
    path('send-to-user/', SendNotificationToUserView.as_view(), name='send-to-user'),
    path('send-to-token/', SendNotificationToTokenView.as_view(),
         name='send-to-token'),
]
