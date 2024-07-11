from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_default.views import retry
from app_site.models import Notification, SiteSettings
from app_site.serializers import NotificationSerializer, SaveSiteSettingsSerializer, SiteSettingsSerializer, UploadSiteSettingsSerializer
from django.db.models import Max

from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.

@csrf_exempt
@swagger_auto_schema(method='PUT', request_body=SiteSettingsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all site Settingss",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CURDSiteSettingsApi(request, pk=""):
    # try:
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
    # except:
    #     return JsonResponse("Invalid", safe=False)
        



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all site Settingss",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def CURDSiteSettingsApiCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
           
            siteSettings = SiteSettings.objects.get(
                    CompanyId=CompanyId)
            siteSettingsSerializer = SiteSettingsSerializer(
                    siteSettings)
            return JsonResponse(siteSettingsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
        

class UploadSiteSettingsImage(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, SiteSettingsId="", *args, **kwargs):
        # try:

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
        # except:
        #     return JsonResponse("Invalid", safe=False)
        



# class UploadSiteSettingsImage(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     @retry(retries=3, delay=2)
#     def post(self, request, SiteSettingsId="", *args, **kwargs):
#         try:
#             site = SiteSettings.objects.get(
#                 SiteSettingsId=SiteSettingsId)
#             try:
#                 if request.data['Logo']:
#                     SiteSettings.objects.get(
#                         SiteSettingsId=SiteSettingsId).Logo.delete(save=True)
#                 if request.data['FavIcon']:
#                     SiteSettings.objects.get(
#                         SiteSettingsId=SiteSettingsId).FavIcon.delete(save=True)
                
#             except:
#                 p=""
#             siteSerializer = UploadSiteSettingsSerializer(
#                 site, data=request.data)
#             if siteSerializer.is_valid():
#                 siteSerializer.save()
#                 return JsonResponse("Uploaded", safe=False)
#             else:
#                 return JsonResponse("", safe=False)
#         except:
#             return JsonResponse("", safe=False)




@swagger_auto_schema(method='GET',operation_description="NOTE: Get all site Settingss",)
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
    




@swagger_auto_schema(method='GET',operation_description="NOTE: Get all notifications",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def GetNotificationByToUser(request, ToUser=""):
    try:
        if request.method == 'GET':
           
            notification = Notification.objects.filter(
                    ToUser=ToUser)
            notificationSerializer = NotificationSerializer(
                    notification,many=True)
            notificationData=[]
            for row in notificationSerializer.data:
                try:
                    staff=Staff.objects.get(StaffId=row['ToUser'])
                    staffSerializer=StaffSerializer(staff)
                    row['ToUserName']=staffSerializer.data['StaffName']
                    row['ToUserImage']=staffSerializer.data['ProfilePhoto']
                except:
                     row['ToUserImage']=""
                     row['ToUserName']=""
                try:
                    fromstaff=Staff.objects.get(StaffId=row['FromUser'])
                    fromstaffSerializer=StaffSerializer(fromstaff)
                    row['FromUserName']=fromstaffSerializer.data['StaffName']
                    row['FromUserImage']=fromstaffSerializer.data['ProfilePhoto']
                except:
                     row['FromUserImage']=""
                     row['FromUserName']=""
                notificationData.append(row)
                     
            return JsonResponse(notificationData, safe=False)
        else:
                return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)