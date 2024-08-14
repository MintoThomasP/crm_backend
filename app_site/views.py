from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_default.views import retry
from app_login.models import LoginHistory
from app_project.models import ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectTaskSerializer
from app_project.views import CustomPageNumberPagination
from app_site.models import Notification, SiteMessage, SiteSettings
from app_site.serializers import NotificationSerializer, SaveSiteSettingsSerializer, SiteMessageSerializer, SiteSettingsSerializer, UploadSiteSettingsSerializer
from django.db.models import Max
from django.db.models import F
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.
from rest_framework import generics

@csrf_exempt
@swagger_auto_schema(method='PUT', request_body=SiteSettingsSerializer,operation_description="NOTE: API for edit SiteSettings")
@swagger_auto_schema(method='POST', request_body=SiteSettingsSerializer,operation_description="NOTE: API for save SiteSettings")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get one site Settingss. (currently not using)",)
@api_view(['GET','POST','PUT'])
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
@swagger_auto_schema(method='GET',operation_description="NOTE:API for Get all site Settingss by CompanyId",)
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
        






@swagger_auto_schema(method='GET',operation_description="NOTE: API for get SiteSettings by SiteSettingsId",)
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
    queryset =Notification.objects.all().order_by('-CreatedDate')
    pagination_class = CustomPageNumberPagination
    serializer_class = NotificationSerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            if filterData['ToUser']:
                self.queryset = self.queryset.filter(ToUser=filterData['ToUser'])

            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                
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
                    data.append(row)
                        
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=SiteMessageSerializer,operation_description="NOTE: API for save SiteMessage")
@swagger_auto_schema(method='PUT', request_body=SiteMessageSerializer,operation_description="NOTE: API for edit SiteMessage")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all SiteMessage",)
@api_view(['GET','POST','PUT'])
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get SiteMessage by SiteMessageId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete SiteMessage by SiteMessageId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def SiteMessageById(request, SiteMessageId=""):
    try:
        if request.method == 'GET':
            siteMessage = SiteMessage.objects.get(SiteMessageId=SiteMessageId)
            siteMessageSerializer = SiteMessageSerializer(siteMessage)
            return JsonResponse(siteMessageSerializer.data, safe=False)
        elif request.method == 'DELETE':
            siteMessage = SiteMessage.objects.get(
                SiteMessageId=SiteMessageId)
            siteMessage.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get SiteMessage by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def SiteMessageByCompanyId(request,CompanyId=""):
    try:
        if request.method == 'GET':
            siteMessage = SiteMessage.objects.filter(CompanyId=CompanyId)
            siteMessageSerializer = SiteMessageSerializer(siteMessage,many=True)
            return JsonResponse(siteMessageSerializer.data, safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    
