
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_default.models import CategoryType, ClientReference, CompanyDocumentType, CountryCode, Currency, DepositTo, EnquiryStatus, EnquiryType, FollowUpStatus, FollowUpType, InvoiceStatus, LeaveStatus, LeaveType, MeetingType, PaymentMode, ReportType, SectionType, StaffStatus,  TaskStatus, UserType
from app_default.serializers import CategoryTypeSerializer, ClientReferenceSerializer, CompanyDocumentTypeSerializer, CountryCodeSerializer, CurrencySerializer, DepositToSerializer, EnquiryStatusSerializer, EnquiryTypeSerializer, FollowUpStatusSerializer, FollowUpTypeSerializer,InvoiceStatusSerializer, LeaveStatusSerializer, LeaveTypeSerializer, MeetingTypeSerializer, PaymentModeSerializer, ReportTypeSerializer, SectionTypeSerializer, StaffStatusSerializer, TaskStatusSerializer, UserTypeSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
import time
from functools import wraps
from django.db import DatabaseError
from rest_framework import serializers
from django.contrib.auth.models import Permission


def retry(retries=3, delay=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(retries):
                try:
                    return func(*args, **kwargs)
                except (DatabaseError, requests.ConnectionError, requests.Timeout) as e:
                    if attempt < retries - 1:
                        time.sleep(delay)
                    else:
                        raise e
        return wrapper
    return decorator




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=TaskStatusSerializer,operation_description="NOTE: API for save TaskStatus")
@swagger_auto_schema(method='PUT', request_body=TaskStatusSerializer,operation_description="NOTE: API for edit TaskStatus")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all task status",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def TaskStatusApi(request):
    try:
        if request.method == 'GET':
            taskStatus = TaskStatus.objects.all()
            taskStatusSerializer = TaskStatusSerializer(
                    taskStatus, many=True)
            return JsonResponse(taskStatusSerializer.data, safe=False)
        elif request.method == 'POST':
            taskStatusData = JSONParser().parse(request)
            taskStatusSerializer = TaskStatusSerializer(
                data=taskStatusData)
            if taskStatusSerializer.is_valid():
                taskStatusSerializer.save()
                return JsonResponse(taskStatusSerializer.data['StatusId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            taskStatusData = JSONParser().parse(request)
            taskStatus = TaskStatus.objects.get(
                StatusId=taskStatusData['StatusId'])
            taskStatusSerializer = TaskStatusSerializer(
                taskStatus, data=taskStatusData)
            if taskStatusSerializer.is_valid():
                taskStatusSerializer.save()
                return JsonResponse(taskStatusSerializer.data['StatusId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get TaskStatus by StatusId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete TaskStatus by StatusId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def TaskStatusApiById(request, StatusId=""):
    try:
        if request.method == 'GET': 
            taskStatus = TaskStatus.objects.get(
                    StatusId=StatusId)
            taskStatusSerializer = TaskStatusSerializer(
                    taskStatus)
            return JsonResponse(taskStatusSerializer.data, safe=False)
        elif request.method == 'DELETE':
            taskStatus = TaskStatus.objects.get(StatusId=StatusId)
            taskStatus.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE:API for get all Usertypes",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def UserTypeApi(request):
    try:
        if request.method == 'GET':
            userType = UserType.objects.all()
            userTypeSerializer = UserTypeSerializer(
                    userType, many=True)
            return JsonResponse(userTypeSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

from django.db import transaction
def get_permissions(request):
    BATCH_SIZE = 100
    permissions = Permission.objects.all()
    total_permission = permissions.count()
    
    all_serialized_data = []
    
    for i in range(0, total_permission, BATCH_SIZE):
        with transaction.atomic():
            batch_tasks = permissions[i:i+BATCH_SIZE]
            serializer = PermissionSerializer(batch_tasks, many=True)
            serialized_data = serializer.data
            all_serialized_data.extend(serialized_data)
    return JsonResponse(all_serialized_data, safe=False)





    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all Currency",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def CurrencyApi(request):
    try:
        if request.method == 'GET':
            currency = Currency.objects.all()
            currency_serializer = CurrencySerializer(
                currency, many=True)  
            return JsonResponse(currency_serializer.data, safe=False)
        else:
            return JsonResponse("",safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all PaymentMode",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def PaymentModeApi(request):
    try:
        if request.method == 'GET':
            paymentMode = PaymentMode.objects.all()
            paymentMode_serializer = PaymentModeSerializer(
                paymentMode, many=True)  
            return JsonResponse(paymentMode_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for  Get all DepositTo",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def DepositToApi(request):
    try:
        if request.method == 'GET':
            depositTo = DepositTo.objects.all()
            depositTo_serializer = DepositToSerializer(
                depositTo, many=True)  
            return JsonResponse(depositTo_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE:API for Get all InvoiceStatus",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def InvoiceStatusApi(request):
    try:
        if request.method == 'GET':
            invoiceStatus = InvoiceStatus.objects.all()
            invoiceStatus_serializer = InvoiceStatusSerializer(
                invoiceStatus, many=True)  
            return JsonResponse(invoiceStatus_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all StaffStatus",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def StaffStatusApi(request):
    try:
        if request.method == 'GET':
            staffStatus = StaffStatus.objects.all()
            staffStatus_serializer = StaffStatusSerializer(
                staffStatus, many=True)  
            return JsonResponse(staffStatus_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all LeaveType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def LeaveTypeApi(request):
    try:
        if request.method == 'GET':
            leaveType = LeaveType.objects.all()
            leaveType_serializer = LeaveTypeSerializer(
                leaveType, many=True)  
            return JsonResponse(leaveType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all LeaveStatus",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def LeaveStatusApi(request):
    try:
        if request.method == 'GET':
            leaveStatus = LeaveStatus.objects.all()
            leaveStatus_serializer = LeaveStatusSerializer(
                leaveStatus, many=True)  
            return JsonResponse(leaveStatus_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all DocumentType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def DocumentTypeApi(request):
    try:
        if request.method == 'GET':
            documentType = CompanyDocumentType.objects.all()
            documentType_serializer = CompanyDocumentTypeSerializer(
                documentType, many=True)  
            return JsonResponse(documentType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    





@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all SectionType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def SectionTypeApi(request):
    try:
        if request.method == 'GET':
            sectionType = SectionType.objects.all()
            sectionType_serializer = SectionTypeSerializer(
                sectionType, many=True)  
            return JsonResponse(sectionType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all CategoryType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def CategoryTypeApi(request):
    try:
        if request.method == 'GET':
            categoryType = CategoryType.objects.all()
            categoryType_serializer = CategoryTypeSerializer(
                categoryType, many=True)  
            return JsonResponse(categoryType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all ReportType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ReportTypeApi(request):
    try:
        if request.method == 'GET':
            reportType = ReportType.objects.all()
            reportType_serializer = ReportTypeSerializer(
                reportType, many=True)  
            return JsonResponse(reportType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all MeetingType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def MeetingTypeApi(request):
    try:
        if request.method == 'GET':
            meetingType = MeetingType.objects.all()
            meetingType_serializer = MeetingTypeSerializer(
                meetingType, many=True)  
            return JsonResponse(meetingType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all EnquiryType",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def EnquiryTypeApi(request):
    try:
        if request.method == 'GET':
            enquiryType = EnquiryType.objects.all()
            enquiryType_serializer = EnquiryTypeSerializer(
                enquiryType, many=True)  
            return JsonResponse(enquiryType_serializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all FollowUpStatus",)
@api_view(['GET'])
def FollowUpStatusApi(request):
    try:
        if request.method == 'GET':
            followUpStatus = FollowUpStatus.objects.all()
            followUpStatusSerializer = FollowUpStatusSerializer(followUpStatus, many=True)
            return JsonResponse(followUpStatusSerializer.data, safe=False)    
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all FollowUpType",)
@api_view(['GET'])
def FollowUpTypeApi(request):
    try:
        if request.method == 'GET':
            followUpType = FollowUpType.objects.all()
            followUpTypeSerializer = FollowUpTypeSerializer(followUpType, many=True)
            return JsonResponse(followUpTypeSerializer.data, safe=False)    
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all VanDeliveryEnquiryStatus",)
@api_view(['GET'])
def EnquiryStatusApi(request):
    try:
        if request.method == 'GET': 
            enquiryStatus = EnquiryStatus.objects.all()
            enquiryStatusSerializer = EnquiryStatusSerializer(enquiryStatus, many=True)
            return JsonResponse(enquiryStatusSerializer.data, safe=False)        
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all CountryCode",)
@api_view(['GET'])
def CountryCodeApi(request):
    try:
        if request.method == 'GET': 
            countryCode = CountryCode.objects.all()
            countryCodeSerializer = CountryCodeSerializer(countryCode, many=True)
            return JsonResponse(countryCodeSerializer.data, safe=False)        
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all ClientReference",)
@api_view(['GET'])
def ClientReferenceApi(request):
    try:
        if request.method == 'GET': 
            clientReference = ClientReference.objects.all()
            clientReferenceSerializer = ClientReferenceSerializer(clientReference, many=True)
            return JsonResponse(clientReferenceSerializer.data, safe=False)        
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all SiteContactType",)
@api_view(['GET'])
def SiteContactTypeApi(request):
    try:
        if request.method == 'GET': 
            siteContactType = SiteContactType.objects.all()
            siteContactTypeSerializer = SiteContactTypeSerializer(siteContactType, many=True)
            return JsonResponse(siteContactTypeSerializer.data, safe=False)        
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("Invalid", safe=False)
