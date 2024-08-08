from django.shortcuts import render
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from app_default.models import EnquiryStatus, EnquiryType, FollowUpStatus, FollowUpType
from app_default.serializers import EnquiryStatusSerializer, EnquiryTypeSerializer, FollowUpStatusSerializer, FollowUpTypeSerializer
from app_default.views import retry
from app_enquiry.models import Enquiry, FollowUp
from app_enquiry.serailizers import EnquirySerializer, FollowUpSerializer
from app_project.views import CustomPageNumberPagination
from rest_framework import generics

from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=EnquirySerializer,operation_description="NOTE: API for save Enquiry")
@swagger_auto_schema(method='PUT', request_body=EnquirySerializer,operation_description="NOTE: API for edit Enquiry")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all Enquiry Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def EnquiryApi(request):
    try:
        if request.method == 'GET':
            enquiry = Enquiry.objects.all()
            enquirySerializer = EnquirySerializer(
                    enquiry, many=True)
            return JsonResponse(enquirySerializer.data, safe=False)
        elif request.method == 'POST':
            enquiryData = JSONParser().parse(request)
            enquirySerializer = EnquirySerializer(
                data=enquiryData)
            if enquirySerializer.is_valid():
                enquirySerializer.save()

                return JsonResponse(enquirySerializer.data['EnquiryId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            enquiryData = JSONParser().parse(request)
            enquiry = Enquiry.objects.get(
                EnquiryId=enquiryData['EnquiryId'])
            enquirySerializer = EnquirySerializer(
                enquiry, data=enquiryData)
            if enquirySerializer.is_valid():
                enquirySerializer.save()
                return JsonResponse(enquirySerializer.data['EnquiryId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Enquiry by EnquiryId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for DELETE Enquiry by EnquiryId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def EnquiryApiById(request, EnquiryId=""):
    try:
        if request.method == 'GET': 
            enquiry = Enquiry.objects.get(
                    EnquiryId=EnquiryId)
            enquirySerializer = EnquirySerializer(
                    enquiry)
            return JsonResponse(enquirySerializer.data, safe=False)
        elif request.method == 'DELETE':
            enquiry = Enquiry.objects.get(EnquiryId=EnquiryId)
            enquiry.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

class EnquiryApiByCompanyId(generics.ListAPIView):
    queryset =Enquiry.objects.all().order_by('-CreatedDate')
    pagination_class = CustomPageNumberPagination
    serializer_class = EnquirySerializer 
    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(CompanyId=filterData['CompanyId'])
            
            if Keyword:
                self.queryset = self.queryset.filter(Description__icontains=Keyword)
            
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        enquiryType = EnquiryType.objects.get(EnquiryTypeId=row['EnquiryType'])
                        enquiryType_serializer = EnquiryTypeSerializer(
                        enquiryType)
                        row['EnquiryTypeName']=enquiryType_serializer.data['EnquiryType']
                    except:
                        row['EnquiryTypeName']=""
                    try:
                        enquiryStatus = EnquiryStatus.objects.get(StatusId=row['Status'])
                        enquiryStatus_serializer = EnquiryStatusSerializer(
                        enquiryStatus)
                        row['EnquiryStatusName']=enquiryStatus_serializer.data['Status']
                    except:
                        row['EnquiryStatusName']=""
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get all FollowUp",)
@swagger_auto_schema(method='POST', request_body=FollowUpSerializer,operation_description="NOTE: API for save FollowUp")
@swagger_auto_schema(method='PUT', request_body=FollowUpSerializer,operation_description="NOTE: API for edit FollowUp")
@api_view(['GET','POST','PUT'])
def CURDFollowUpApi(request):
    try:
        if request.method == 'GET':
            followUp = FollowUp.objects.all().order_by('-SortId')
            followUpSerializer = FollowUpSerializer(
                followUp, many=True)
            return JsonResponse(followUpSerializer.data, safe=False)
      
        elif request.method == 'POST':
            followUpData = JSONParser().parse(request)
            followUpSerializer = FollowUpSerializer(
                data=followUpData)
            if followUpSerializer.is_valid():
                followUpSerializer.save()
                return JsonResponse(followUpSerializer.data['FollowUpId'], safe=False)
            return JsonResponse("Failed", safe=False)
        elif request.method == 'PUT':
            followUpData = JSONParser().parse(request)
            followUp = FollowUp.objects.get(
                FollowUpId=followUpData['FollowUpId'])
            followUpSerializer = FollowUpSerializer(
                followUp, data=followUpData)
            if followUpSerializer.is_valid():
                followUpSerializer.save()
                return JsonResponse(followUpSerializer.data['FollowUpId'], safe=False)
            return JsonResponse("Failed", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get FollowUp by FollowUpId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for DELETE FollowUp by FollowUpId",)
@api_view(['GET','DELETE'])
def CURDFollowUpApiById(request, FollowUpId=""):
    try:
        if request.method == 'GET':
            followUp = FollowUp.objects.get(FollowUpId=FollowUpId)
            followUpSerializer = FollowUpSerializer(
                followUp)
         
            return JsonResponse(followUpSerializer.data, safe=False)    
        elif request.method == 'DELETE':
             followUp = FollowUp.objects.get(FollowUpId=FollowUpId)
             followUp.delete()
             return JsonResponse("Deleted successfully",safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get FollowUp by EnquiryId",)
@api_view(['GET'])
def CURDFollowUpApiByEnquiryId(request, EnquiryId=""):
    try:
        if request.method == 'GET':
            followUp = FollowUp.objects.filter(EnquiryId=EnquiryId)
            followUpSerializer = FollowUpSerializer(
                followUp,many=True)
            followUpData=[]
            for row in followUpSerializer.data:
                try:
                    staff=Staff.objects.get(StaffId=row['ScheduledBy'])
                    staffSerializer=StaffSerializer(staff)
                    row['ScheduledByName']=staffSerializer.data['StaffName']
                except:
                    row['ScheduledByName']=""
                try:
                    staff=Staff.objects.get(StaffId=row['UserId'])
                    staffSerializer=StaffSerializer(staff)
                    row['UserName']=staffSerializer.data['StaffName']
                except:
                    row['UserName']=""
                try:
                    status=FollowUpStatus.objects.get(StatusId=row['Status'])
                    statusSerializer=FollowUpStatusSerializer(status)
                    row['StatusName']=statusSerializer.data['Status']
                except:
                    row['StatusName']=""
                try:
                    type=FollowUpType.objects.get(FollowUpTypeId=row['FollowUpType'])
                    typeSerializer=FollowUpTypeSerializer(type)
                    row['FollowUpTypeName']=typeSerializer.data['FollowUpType']
                except:
                    row['FollowUpTypeName']=""
                followUpData.append(row)
            return JsonResponse(followUpData, safe=False)    
       
    except:
        return JsonResponse("Invalid", safe=False)
    