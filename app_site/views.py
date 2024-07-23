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
from app_site.models import Notification, SiteSettings
from app_site.serializers import NotificationSerializer, SaveSiteSettingsSerializer, SiteSettingsSerializer, UploadSiteSettingsSerializer
from django.db.models import Max
from django.db.models import F
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
                    ToUser=ToUser).order_by(F('CreatedDate').desc())[:50]
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
    


from datetime import datetime, timedelta, timezone
@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: Get all site Settings")
@api_view(['GET'])
@retry(retries=3, delay=2)
def dateconversion(request):
    if request.method == 'GET':
        dateconversionProjectTask()
        dateconversionProjectTaskTiming()
        dateconversionLoginHistory()
        

        return JsonResponse("Updated", safe=False)
    else:
        return JsonResponse("", safe=False)
    



def dateconversionProjectTask():
    projecttask = ProjectTask.objects.all()
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
        '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
        '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
        '%d/%m/%Y, %H:%M:%S',     # Example: 07/04/2024, 10:06:38,
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]

    timezone_offset = timedelta(hours=5, minutes=30)
    tz_info = timezone(timezone_offset)

    def parse_and_format(date_str):
        for date_format in date_formats:
            try:
                parsed_datetime = datetime.strptime(date_str, date_format)
                parsed_datetime = parsed_datetime.replace(tzinfo=tz_info)
                formatted_datetime = parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
                formatted_datetime = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
                return formatted_datetime
            except ValueError:
                continue
        return None

    for row in projecttask:
        if row.StartDate:
            formatted_startdate = parse_and_format(row.StartDate)
            if formatted_startdate:
                row.StartDate = formatted_startdate

        if row.EndDate:
            formatted_enddate = parse_and_format(row.EndDate)
            if formatted_enddate:
                row.EndDate = formatted_enddate

        if row.ScheduledDeadline:
            formatted_deadline = parse_and_format(row.ScheduledDeadline)
            if formatted_deadline:
                row.ScheduledDeadline = formatted_deadline

        row.save()

             

def dateconversionProjectTaskTiming():
    projecttask = ProjectTaskTiming.objects.all()
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
        '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
        '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
        '%d/%m/%Y, %H:%M:%S',     # Example: 07/04/2024, 10:06:38,
        "%Y-%m-%dT%H:%M:%S%z"
    ]

    timezone_offset = timedelta(hours=5, minutes=30)
    tz_info = timezone(timezone_offset)

    def parse_and_format(date_str):
        for date_format in date_formats:
            try:
                parsed_datetime = datetime.strptime(date_str, date_format)
                parsed_datetime = parsed_datetime.replace(tzinfo=tz_info)
                formatted_datetime = parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
                formatted_datetime = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
                return formatted_datetime
            except ValueError:
                continue
        return None

    for row in projecttask:
        if row.StartDate:
            formatted_startdate = parse_and_format(row.StartDate)
            if formatted_startdate:
                row.StartDate = formatted_startdate

        if row.EndDate:
            formatted_enddate = parse_and_format(row.EndDate)
            if formatted_enddate:
                row.EndDate = formatted_enddate

        row.save()



def dateconversionLoginHistory():
    projecttask = LoginHistory.objects.all()
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
        '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
        '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
        '%d/%m/%Y, %H:%M:%S',     # Example: 07/04/2024, 10:06:38,
        "%Y-%m-%dT%H:%M:%S%z"
    ]

    timezone_offset = timedelta(hours=5, minutes=30)
    tz_info = timezone(timezone_offset)

    def parse_and_format(date_str):
        for date_format in date_formats:
            try:
                parsed_datetime = datetime.strptime(date_str, date_format)
                parsed_datetime = parsed_datetime.replace(tzinfo=tz_info)
                formatted_datetime = parsed_datetime.strftime('%Y-%m-%dT%H:%M:%S%z')
                formatted_datetime = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
                return formatted_datetime
            except ValueError:
                continue
        return None

    for row in projecttask:
        if row.LoginTime:
            formatted_startdate = parse_and_format(row.LoginTime)
            if formatted_startdate:
                row.LoginTime = formatted_startdate

        if row.LogoutTime:
            formatted_enddate = parse_and_format(row.LogoutTime)
            if formatted_enddate:
                row.LogoutTime = formatted_enddate

        row.save()