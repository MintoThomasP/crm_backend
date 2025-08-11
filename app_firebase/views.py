
from django.conf import settings
from app_site.serializers import NotificationSerializer
import firebase_admin
from app_firebase.serailizers import DeviceTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DeviceToken
from firebase_admin import credentials, messaging


class DeviceTokenCreateView(APIView):
    # Accepts { UserId: "123", Token: "..." }
    def post(self, request):
        UserId = request.data.get('UserId')
        Token = request.data.get('Token')
        UserType = request.data.get('UserType')
        if not Token:
            return Response({"detail": "Token is required"}, status=status.HTTP_400_BAD_REQUEST)

        # create or update
        obj, created = DeviceToken.objects.update_or_create(
            Token=Token,
            defaults={'UserId': UserId, 'Active': True, UserType: UserType}
        )
        serializer = DeviceTokenSerializer(obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SendNotificationToUserView(APIView):
    # POST { "UserId": "123", "title": "...", "body": "...", "data": {...} }
    def post(self, request):
        FormUserId = request.data.get('FormUserId')
        ToUserId = request.data.get('ToUserId')
        title = request.data.get('Title')
        body = request.data.get('Body')
        data = request.data.get('Data', {})

        if not ToUserId or not title or not body:
            return Response({"detail": "UserId, title and body required"}, status=status.HTTP_400_BAD_REQUEST)

        Tokens = DeviceToken.objects.filter(
            UserId=ToUserId, Active=True).values_list('Token', flat=True)
        if not Tokens:
            return Response({"detail": "No Tokens found for user"}, status=status.HTTP_404_NOT_FOUND)

        results = []
        for Token in Tokens:
            data.update(
                icon="https://crm-api-live.cubexizsoft.com/media/FavIcon/11722800570325.webp")
            try:
                resp = send_message_to_Token(Token, title, body, data)
                results.append({"Token": Token, "response": resp})

            except Exception as e:
                results.append({"Token": Token, "error": str(e)})

            notificationdata = {
                "Title": title,
                "Message": body,
                "FromUser": FormUserId,
                "ToUser": ToUserId,
            }
            notificationSerializer = NotificationSerializer(
                data=notificationdata)
            if notificationSerializer.is_valid():
                notificationSerializer.save()
        return Response({"results": results})

# optional: send to specific Token


class SendNotificationToTokenView(APIView):
    def post(self, request):
        Token = request.data.get('Token')
        title = request.data.get('title')
        body = request.data.get('body')
        data = request.data.get('data', {})

        if not Token or not title or not body:
            return Response({"detail": "Token, title and body required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            resp = send_message_to_Token(Token, title, body, data)

            return Response({"response": resp})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


firebase_app = None


def init_firebase():
    global firebase_app
    if firebase_app:
        return firebase_app

    cred_path = getattr(settings, 'FIREBASE_SERVICE_ACCOUNT_PATH', None)
    if not cred_path:
        raise Exception("FIREBASE_SERVICE_ACCOUNT_PATH not set in settings.py")

    cred = credentials.Certificate(str(cred_path))
    firebase_app = firebase_admin.initialize_app(cred)
    return firebase_app

# optional helper to send message


def send_message_to_Token(Token: str, title: str, body: str, data: dict = None):
    init_firebase()
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=Token,
        data=data or {}
    )
    response = messaging.send(message)

    return response
