from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from app_site.models import SiteSettings
from app_site.serializers import SiteSettingsSerializer
from django.db.models import Max
# Create your views here.

@csrf_exempt
@swagger_auto_schema(method='PUT', request_body=SiteSettingsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all site Settingss",)
@api_view(['GET','POST','PUT'])
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
            siteSettingsSerializer = SiteSettingsSerializer(
                data=siteSettingsData)
            if siteSettingsSerializer.is_valid():
                siteSettingsSerializer.save()
                return JsonResponse(siteSettingsSerializer.data['SiteSettingsId'], safe=False)
            return JsonResponse("Failed", safe=False)
        elif request.method == 'PUT':
            siteSettingsData = JSONParser().parse(request)
            siteSettings = SiteSettings.objects.get(
                SiteSettingsId=siteSettingsData['SiteSettingsId'])
            siteSettingsSerializer = SiteSettingsSerializer(
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
        