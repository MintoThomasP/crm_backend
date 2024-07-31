
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import requests
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from app_default.models import CategoryType, CompanyDocumentType, Country, Currency, DepositTo, Designation, EnquiryStatus, EnquiryType, FollowUpStatus, FollowUpType, InvoiceStatus, LeaveStatus, LeaveType, MeetingType, PaymentMode, ReportType, SectionType, StaffStatus, State, TaskStatus, UserGroup, UserType
from app_default.serializers import CategoryTypeSerializer, CompanyDocumentTypeSerializer, CountrySerializer, CurrencySerializer, DepositToSerializer, DesignationSerializer, EnquiryStatusSerializer, EnquiryTypeSerializer, FollowUpStatusSerializer, FollowUpTypeSerializer,InvoiceStatusSerializer, LeaveStatusSerializer, LeaveTypeSerializer, MeetingTypeSerializer, PaymentModeSerializer, ReportTypeSerializer, SectionTypeSerializer, StaffStatusSerializer, StateSerializer, TaskStatusSerializer, UserGroupSerializer, UserTypeSerializer
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
@swagger_auto_schema(method='POST', request_body=TaskStatusSerializer)
@swagger_auto_schema(method='PUT', request_body=TaskStatusSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all task status",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: Give StatusId to get one status",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: get all Usertypes",)
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
@swagger_auto_schema(method='POST', request_body=UserGroupSerializer)
@swagger_auto_schema(method='PUT', request_body=UserGroupSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Usergroup Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def UserGroupApi(request):
    try:
        if request.method == 'GET':
            userGroup = UserGroup.objects.all()
            userGroup_serializer = UserGroupSerializer(
                userGroup, many=True)
            
            return JsonResponse(userGroup_serializer.data, safe=False)

        elif request.method == 'POST':
            userGroupData = JSONParser().parse(request)
            userGroupSerializer = UserGroupSerializer(
                data=userGroupData)
            if userGroupSerializer.is_valid():
                userGroupSerializer.save()
                return JsonResponse(userGroupSerializer.data['UserGroupId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            userGroupData = JSONParser().parse(request)
            userGroup = UserGroup.objects.get(
                UserGroupId=userGroupData['UserGroupId'])
            userGroupSerializer = UserGroupSerializer(
                userGroup, data=userGroupData)
            if userGroupSerializer.is_valid():
                userGroupSerializer.save()
                return JsonResponse(userGroupSerializer.data['UserGroupId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give UserGroupId to get one detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def UserGroupApiById(request, UserGroupId=""):
    # try:
        if request.method == 'GET':
            userGroup = UserGroup.objects.get(UserGroupId=UserGroupId)
            userGroup_serializer = UserGroupSerializer(userGroup)
            return JsonResponse(userGroup_serializer.data, safe=False)
        elif request.method == 'DELETE':
            userGroup = UserGroup.objects.get(
                UserGroupId=UserGroupId)
            userGroup.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=DesignationSerializer)
@swagger_auto_schema(method='PUT', request_body=DesignationSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Designation Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def DesignationApi(request):
    try:
        if request.method == 'GET':
            designation = Designation.objects.all()
            designation_serializer = DesignationSerializer(
                designation, many=True)  
            return JsonResponse(designation_serializer.data, safe=False)

        elif request.method == 'POST':
            designationData = JSONParser().parse(request)
            # return JsonResponse(designationData, safe=False)
            designationSerializer = DesignationSerializer(
                data=designationData)
            if designationSerializer.is_valid():
                designationSerializer.save()
                return JsonResponse(designationSerializer.data['DesignationId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            designationData = JSONParser().parse(request)
            designation = Designation.objects.get(
                DesignationId=designationData['DesignationId'])
            designationSerializer = DesignationSerializer(
                designation, data=designationData)
            if designationSerializer.is_valid():
                designationSerializer.save()
                return JsonResponse(designationSerializer.data['DesignationId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give DesignationId to get one detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def DesignationApiById(request, DesignationId=""):
    try:
        if request.method == 'GET':
            designation = Designation.objects.get(DesignationId=DesignationId)
            designationSerializer = DesignationSerializer(designation)
            return JsonResponse(designationSerializer.data, safe=False)
        elif request.method == 'DELETE':
            designation = Designation.objects.get(
                DesignationId=DesignationId)
            designation.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Currency Details",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all PaymentMode Details",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all DepositTo Details",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all InvoiceStatus Details",)
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
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CountrySerializer)
@swagger_auto_schema(method='PUT', request_body=CountrySerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Country Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def CountryApi(request):
    try:
        if request.method == 'GET':
            country = Country.objects.all()
            country_serializer = CountrySerializer(
                country, many=True)  
            return JsonResponse(country_serializer.data, safe=False)

        elif request.method == 'POST':
            countryData = JSONParser().parse(request)
            countrySerializer = CountrySerializer(
                data=countryData)
            if countrySerializer.is_valid():
                countrySerializer.save()
                return JsonResponse(countrySerializer.data['CountryId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            countryData = JSONParser().parse(request)
            country = Country.objects.get(
                CountryId=countryData['CountryId'])
            countrySerializer = CountrySerializer(
                country, data=countryData)
            if countrySerializer.is_valid():
                countrySerializer.save()
                return JsonResponse(countrySerializer.data['CountryId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CountryId to get one detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def CountryApiById(request, CountryId=""):
    try:
        if request.method == 'GET':
            country = Country.objects.get(CountryId=CountryId)
            countrySerializer = CountrySerializer(country)
            return JsonResponse(countrySerializer.data, safe=False)
        elif request.method == 'DELETE':
            country = Country.objects.get(
                CountryId=CountryId)
            country.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StateSerializer)
@swagger_auto_schema(method='PUT', request_body=StateSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all State Details",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def StateApi(request):
    try:
        if request.method == 'GET':
            state = State.objects.all()
            state_serializer = StateSerializer(
                state, many=True)  
            return JsonResponse(state_serializer.data, safe=False)

        elif request.method == 'POST':
            stateData = JSONParser().parse(request)
            stateSerializer = StateSerializer(
                data=stateData)
            if stateSerializer.is_valid():
                stateSerializer.save()
                return JsonResponse(stateSerializer.data['StateId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            stateData = JSONParser().parse(request)
            state = State.objects.get(
                StateId=stateData['StateId'])
            stateSerializer = StateSerializer(
                state, data=stateData)
            if stateSerializer.is_valid():
                stateSerializer.save()
                return JsonResponse(stateSerializer.data['StateId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give StateId to get one detail",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def StateApiById(request, StateId=""):
    try:
        if request.method == 'GET':
            state = State.objects.get(StateId=StateId)
            stateSerializer = StateSerializer(state)
            return JsonResponse(stateSerializer.data, safe=False)
        elif request.method == 'DELETE':
            state = State.objects.get(
                StateId=StateId)
            state.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@swagger_auto_schema(method='GET',operation_description="NOTE: Get all State by CountryId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def StateApiByCountryId(request,CountryId=""):
    try:
        if request.method == 'GET':
            state = State.objects.filter(CountryId=CountryId)
            state_serializer = StateSerializer(
                state, many=True)  
            return JsonResponse(state_serializer.data, safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all StaffStatus Details",)
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
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all LeaveType Details",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all LeaveStatus Details",)
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
        return JsonResponse("Invalid", safe=False)
    
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all DocumentType Details",)
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
        return JsonResponse("Invalid", safe=False)
    





@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all SectionType Details",)
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
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all CategoryType Details",)
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
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all ReportType Details",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all MeetingType Details",)
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
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all EnquiryType Details",)
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
        return JsonResponse("Invalid", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all FollowUpStatus",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all FollowUpType",)
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
        return JsonResponse("Invalid", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all VanDeliveryEnquiryStatus",)
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
        return JsonResponse("Invalid", safe=False)