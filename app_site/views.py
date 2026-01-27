import json
import requests
import datetime
import base64
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_default.models import SiteContactType
from app_default.serializers import SiteContactTypeSerializer
from app_default.views import retry
from app_login.models import LoginHistory
from app_project.models import ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectTaskSerializer
from app_project.views import CustomPageNumberPagination
from app_site.models import Notification, SiteContact, SiteMessage, SiteSettings
from app_site.serializers import NotificationSerializer, SaveSiteSettingsSerializer, SiteContactSerializer, SiteMessageSerializer, SiteSettingsSerializer, UploadSiteSettingsSerializer
from django.db.models import Max
from django.db.models import F
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.
from rest_framework import generics


@swagger_auto_schema(method='GET', operation_description="NOTE: API for check network connection",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def checkNetwork(request):
    if request.method == 'GET':
        return JsonResponse("Ok", safe=False)


@csrf_exempt
@swagger_auto_schema(method='PUT', request_body=SiteSettingsSerializer, operation_description="NOTE: API for edit SiteSettings")
@swagger_auto_schema(method='POST', request_body=SiteSettingsSerializer, operation_description="NOTE: API for save SiteSettings")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get one site Settingss. (currently not using)",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def CURDSiteSettingsApi(request, pk=""):
    try:
        if request.method == 'GET':
            last_id = SiteSettings.objects.aggregate(
                Max('SiteSettingsId'))['SiteSettingsId__max']
            siteSettings = SiteSettings.objects.get(
                SiteSettingsId=last_id)
            siteSettingsSerializer = SiteSettingsSerializer(
                siteSettings)
            return JsonResponse(siteSettingsSerializer.data, safe=False)
        elif request.method == 'POST':
            siteSettingsData = JSONParser().parse(request)

            siteSettingsSerializer = SaveSiteSettingsSerializer(
                data=siteSettingsData)
            if siteSettingsSerializer.is_valid():
                siteSettingsSerializer.save()
                return JsonResponse(siteSettingsSerializer.data['SiteSettingsId'], safe=False)
            return JsonResponse("Failed", safe=False)
        elif request.method == 'PUT':
            siteSettingsData = JSONParser().parse(request)
            siteSettings = SiteSettings.objects.get(
                SiteSettingsId=siteSettingsData['SiteSettingsId'])
            siteSettingsSerializer = SaveSiteSettingsSerializer(
                siteSettings, data=siteSettingsData)
            if siteSettingsSerializer.is_valid():
                siteSettingsSerializer.save()
                return JsonResponse(siteSettingsSerializer.data['SiteSettingsId'], safe=False)
            return JsonResponse("Failed", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE:API for Get all site Settingss by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def CURDSiteSettingsApiCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            try:
                siteSettings = SiteSettings.objects.get(
                    CompanyId=CompanyId)
                siteSettingsSerializer = SiteSettingsSerializer(
                    siteSettings)
                siteData = siteSettingsSerializer.data
            except:
                siteData = []

            return JsonResponse(siteData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class UploadSiteSettingsImage(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, SiteSettingsId="", *args, **kwargs):
        try:

            projectTaskFile = SiteSettings.objects.get(
                SiteSettingsId=SiteSettingsId)
            try:
                if request.data['Logo']:
                    SiteSettings.objects.get(
                        SiteSettingsId=SiteSettingsId).Logo.delete(save=True)
                if request.data['FavIcon']:
                    SiteSettings.objects.get(
                        SiteSettingsId=SiteSettingsId).FavIcon.delete(save=True)

            except:
                p = ""
            Serializer = UploadSiteSettingsSerializer(
                projectTaskFile, data=request.data)
            if Serializer.is_valid():
                Serializer.save()
                return JsonResponse("Uploaded", safe=False)
            else:
                return JsonResponse("", safe=False)
        except:
            return JsonResponse("Invalid", safe=False)


@swagger_auto_schema(method='GET', operation_description="NOTE: API for get SiteSettings by SiteSettingsId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def CURDSiteSettingsApiById(request, SiteSettingsId=""):
    try:
        if request.method == 'GET':

            siteSettings = SiteSettings.objects.get(
                SiteSettingsId=SiteSettingsId)
            siteSettingsSerializer = SiteSettingsSerializer(
                siteSettings)
            return JsonResponse(siteSettingsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class GetNotificationByToUser(generics.ListAPIView):
    queryset = Notification.objects.all().order_by('-CreatedDate')
    pagination_class = CustomPageNumberPagination
    serializer_class = NotificationSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            if filterData['ToUser']:
                self.queryset = self.queryset.filter(
                    ToUser=filterData['ToUser'])

            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:

                    try:
                        staff = Staff.objects.get(StaffId=row['ToUser'])
                        staffSerializer = StaffSerializer(staff)
                        row['ToUserName'] = staffSerializer.data['StaffName']
                        row['ToUserImage'] = staffSerializer.data['ProfilePhoto']
                    except:
                        row['ToUserImage'] = ""
                        row['ToUserName'] = ""
                    try:
                        fromstaff = Staff.objects.get(StaffId=row['FromUser'])
                        fromstaffSerializer = StaffSerializer(fromstaff)
                        row['FromUserName'] = fromstaffSerializer.data['StaffName']
                        row['FromUserImage'] = fromstaffSerializer.data['ProfilePhoto']
                    except:
                        row['FromUserImage'] = ""
                        row['FromUserName'] = ""
                    data.append(row)

                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=SiteMessageSerializer, operation_description="NOTE: API for save SiteMessage")
@swagger_auto_schema(method='PUT', request_body=SiteMessageSerializer, operation_description="NOTE: API for edit SiteMessage")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all SiteMessage",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def CURDSiteMessage(request):
    # try:
    if request.method == 'POST':
        siteMessageData = JSONParser().parse(request)
        # return JsonResponse(siteMessageData, safe=False)
        siteMessageSerializer = SiteMessageSerializer(
            data=siteMessageData)
        if siteMessageSerializer.is_valid():
            siteMessageSerializer.save()
            return JsonResponse(siteMessageSerializer.data['SiteMessageId'], safe=False)
        return JsonResponse("Failed to add", safe=False)
    elif request.method == 'PUT':
        siteMessageData = JSONParser().parse(request)
        siteMessage = SiteMessage.objects.get(
            SiteMessageId=siteMessageData['SiteMessageId'])
        siteMessageSerializer = SiteMessageSerializer(
            siteMessage, data=siteMessageData)
        if siteMessageSerializer.is_valid():
            siteMessageSerializer.save()
            return JsonResponse(siteMessageSerializer.data['SiteMessageId'], safe=False)
        return JsonResponse("Failed to Update", safe=False)
    else:
        return JsonResponse("Invalid request", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get SiteMessage by SiteMessageId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete SiteMessage by SiteMessageId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def SiteMessageById(request, CompanyId="", SiteMessageId=""):
    try:
        if request.method == 'GET':
            siteMessage = SiteMessage.objects.get(
                CompanyId=CompanyId, SiteMessageId=SiteMessageId)
            siteMessageSerializer = SiteMessageSerializer(siteMessage)
            return JsonResponse(siteMessageSerializer.data, safe=False)
        elif request.method == 'DELETE':
            siteMessage = SiteMessage.objects.get(CompanyId=CompanyId,
                                                  SiteMessageId=SiteMessageId)
            siteMessage.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get SiteMessage by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def SiteMessageByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            siteMessage = SiteMessage.objects.filter(CompanyId=CompanyId)
            siteMessageSerializer = SiteMessageSerializer(
                siteMessage, many=True)
            return JsonResponse(siteMessageSerializer.data, safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=SiteContactSerializer, operation_description="NOTE: API for save SiteContact")
@swagger_auto_schema(method='PUT', request_body=SiteContactSerializer, operation_description="NOTE: API for edit SiteContact")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all Site contacts",)
@api_view(['GET', 'POST', 'PUT'])
def CURDSiteContactApi(request, pk=""):
    try:
        if request.method == 'GET':
            siteContact = SiteContact.objects.all().order_by('-SortId')
            siteContactSerializer = SiteContactSerializer(
                siteContact, many=True)
            contactData = []
            for row in siteContactSerializer.data:
                try:
                    contactType = SiteContactType.objects.get(
                        ContactTypeId=row['ContactType'])
                    contactTypeSerializer = SiteContactTypeSerializer(
                        contactType)
                    row['ContactTypeName'] = contactTypeSerializer.data['ContactType']
                except:
                    row['ContactTypeName'] = ""
                contactData.append(row)
            return JsonResponse(contactData, safe=False)
        elif request.method == 'POST':
            siteContactData = JSONParser().parse(request)
            siteContactSerializer = SiteContactSerializer(
                data=siteContactData)
            if siteContactSerializer.is_valid():
                siteContactSerializer.save()
                return JsonResponse(siteContactSerializer.data['SiteContactId'], safe=False)
            return JsonResponse("Failed", safe=False)
        elif request.method == 'PUT':
            siteContactData = JSONParser().parse(request)
            siteContact = SiteContact.objects.get(
                SiteContactId=siteContactData['SiteContactId'])
            siteContactSerializer = SiteContactSerializer(
                siteContact, data=siteContactData)
            if siteContactSerializer.is_valid():
                siteContactSerializer.save()
                return JsonResponse(siteContactSerializer.data['SiteContactId'], safe=False)
            return JsonResponse("Failed", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: Api for get SiteContact by SiteContactId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: Api for DELETE SiteContact by SiteContactId",)
@api_view(['GET', 'DELETE'])
def CURDSiteContactApiById(request, SiteContactId=""):
    try:
        if request.method == 'GET':
            siteContact = SiteContact.objects.get(
                SiteContactId=SiteContactId)
            siteContactSerializer = SiteContactSerializer(
                siteContact)
            return JsonResponse(siteContactSerializer.data, safe=False)
        elif request.method == 'DELETE':
            siteContact = SiteContact.objects.get(SiteContactId=SiteContactId)
            siteContact.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)


# Microsoft Graph Configuration
MS_CONFIG = {
    "tenant_id": "22ed5850-9cb2-404c-b644-a0f2987881fb",
    "client_id": "ab3e8431-9019-4d60-ae79-9511ead4705d",
    "client_secret": "REMOVED_AZURE_SECRET",
    "scope": "https://graph.microsoft.com/.default",
    "sender_email": "connect@mintothomas.com",
    "recipient_email": "mintothomas.p@gmail.com",
    # Update this path to where your logo is stored in your Django static files
    "logo_path": "assets/images/logo.png"
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #0a0a0a; padding: 30px; text-align: center; border-bottom: 4px solid #FF4D00; }}
        .logo {{ height: 40px; width: auto; }}
        .content {{ padding: 40px; }}
        .title {{ font-size: 24px; font-weight: bold; color: #0a0a0a; margin-bottom: 20px; border-bottom: 2px solid #eee; padding-bottom: 10px; }}
        .field {{ margin-bottom: 15px; }}
        .label {{ font-weight: bold; color: #FF4D00; text-transform: uppercase; font-size: 12px; letter-spacing: 1px; display: block; margin-bottom: 5px; }}
        .value {{ font-size: 16px; color: #555; }}
        .message-box {{ background: #f9f9f9; padding: 20px; border-radius: 5px; border-left: 4px solid #FF4D00; margin-top: 20px; font-style: italic; }}
        .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <img src="cid:logo_cid" alt="Minto Thomas Logo" class="logo">
        </div>
        <div class="content">
            <div class="title">New Inquiry from Portfolio</div>
            <div class="field"><span class="label">From</span><span class="value">{name}</span></div>
            <div class="field"><span class="label">Email Address</span><span class="value">{email}</span></div>
            <div class="field"><span class="label">Message</span><div class="message-box">{message}</div></div>
        </div>
        <div class="footer">&copy; {year} Minto Thomas Portfolio. All rights reserved.</div>
    </div>
</body>
</html>
"""

THANK_YOU_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4; }}
        .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
        .header {{ background-color: #0a0a0a; padding: 30px; text-align: center; border-bottom: 4px solid #FF4D00; }}
        .logo {{ height: 40px; width: auto; }}
        .content {{ padding: 40px; text-align: center; }}
        .title {{ font-size: 24px; font-weight: bold; color: #0a0a0a; margin-bottom: 20px; }}
        .message {{ font-size: 16px; color: #555; margin-bottom: 30px; }}
        .btn {{ background-color: #FF4D00; color: #ffffff !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block; }}
        .footer {{ background: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #999; border-top: 1px solid #eee; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header"><img src="cid:logo_cid" alt="Minto Thomas Logo" class="logo"></div>
        <div class="content">
            <div class="title">Thank You, {name}!</div>
            <p class="message">I've received your message and will get back to you as soon as possible.</p>
            <div style="margin-bottom: 30px;"><a href="https://mintothomas.com" class="btn">Visit Website</a></div>
            <p class="message" style="font-size: 14px;">Talk soon,<br><strong>Minto Thomas</strong></p>
        </div>
        <div class="footer">&copy; {year} Minto Thomas Portfolio. All rights reserved.</div>
    </div>
</body>
</html>
"""


def get_access_token():
    url = f"https://login.microsoftonline.com/{MS_CONFIG['tenant_id']}/oauth2/v2.0/token"
    data = {
        'client_id': MS_CONFIG['client_id'],
        'scope': MS_CONFIG['scope'],
        'client_secret': MS_CONFIG['client_secret'],
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json().get('access_token')


def send_ms_graph_email(to_email, subject, body_html, logo_base64=None):
    token = get_access_token()
    url = f"https://graph.microsoft.com/v1.0/users/{MS_CONFIG['sender_email']}/sendMail"

    email_data = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": body_html},
            "toRecipients": [{"emailAddress": {"address": to_email}}],
            "attachments": [{
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": "logo.png",
                "contentType": "image/png",
                "contentBytes": logo_base64,
                "contentId": "logo_cid",
                "isInline": True
            }] if logo_base64 else []
        },
        "saveToSentItems": "false"
    }

    headers = {'Authorization': f'Bearer {token}',
               'Content-Type': 'application/json'}
    return requests.post(url, json=email_data, headers=headers)


@csrf_exempt
@api_view(['POST'])
def send_contact_email(request):
    try:
        data = request.data
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')

        if not all([name, email, message]):
            return JsonResponse({"status": "error", "message": "Missing fields"}, status=400)

        year = datetime.datetime.now().year

        # Prepare Logo
        logo_base64 = ""
        try:
            with open(MS_CONFIG["logo_path"], "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Logo error: {e}")

        # 1. Send Inquiry
        inquiry_html = HTML_TEMPLATE.format(
            name=name, email=email, message=message.replace('\n', '<br>'), year=year)
        inquiry_res = send_ms_graph_email(
            MS_CONFIG['recipient_email'], f"New Inquiry from {name}", inquiry_html, logo_base64)

        # 2. Send Thank You
        thank_you_html = THANK_YOU_TEMPLATE.format(name=name, year=year)
        thank_you_res = send_ms_graph_email(
            email, f"Thank you for contacting me, {name}!", thank_you_html, logo_base64)

        if inquiry_res.status_code == 202:
            return JsonResponse({"status": "success", "message": "Emails sent successfully"})
        else:
            return JsonResponse({"status": "error", "message": "Failed to send inquiry email"}, status=500)

    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
