from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_default.models import City, Country, Currency, DepositTo, Designation, InvoiceStatus, PaymentMode, State, TaskStatus, UserGroup, UserType
from app_default.serializers import CitySerializer, CountrySerializer, CurrencySerializer, DepositToSerializer, DesignationSerializer, InvoiceStatusSerializer, PaymentModeSerializer, StateSerializer, TaskStatusSerializer, UserGroupSerializer, UserTypeSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=TaskStatusSerializer)
@swagger_auto_schema(method='PUT', request_body=TaskStatusSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all task status",)
@api_view(['GET','POST','PUT'])
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
    



from rest_framework import serializers
from django.contrib.auth.models import Permission

class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

# Example of usage in a view or API endpoint
def get_permissions(request):
    permissions = Permission.objects.all()
    serializer = PermissionSerializer(permissions, many=True)
    serialized_data = serializer.data

    # You can return the serialized data as a JSON response
    return JsonResponse(serialized_data,safe=False)




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=UserGroupSerializer)
@swagger_auto_schema(method='PUT', request_body=UserGroupSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Usergroup Details",)
@api_view(['GET','POST','PUT'])
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
        return JsonResponse("Invalid payload", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give UserGroupId to get one detail",)
@api_view(['GET','DELETE'])
def UserGroupApiById(request, UserGroupId=""):
    try:
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
    except:
        return JsonResponse("Invalid payload", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=DesignationSerializer)
@swagger_auto_schema(method='PUT', request_body=DesignationSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Designation Details",)
@api_view(['GET','POST','PUT'])
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
        return JsonResponse("Invalid payload", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give DesignationId to get one detail",)
@api_view(['GET','DELETE'])
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
        return JsonResponse("Invalid payload", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Currency Details",)
@api_view(['GET'])
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
        return JsonResponse("Invalid payload", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CountryId to get one detail",)
@api_view(['GET','DELETE'])
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
        return JsonResponse("Invalid payload", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CitySerializer)
@swagger_auto_schema(method='PUT', request_body=CitySerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all City Details",)
@api_view(['GET','POST','PUT'])
def CityApi(request):
    try:
        if request.method == 'GET':
            city = City.objects.all()
            city_serializer = CitySerializer(
                city, many=True)  
            return JsonResponse(city_serializer.data, safe=False)

        elif request.method == 'POST':
            cityData = JSONParser().parse(request)
            citySerializer = CitySerializer(
                data=cityData)
            if citySerializer.is_valid():
                citySerializer.save()
                return JsonResponse(citySerializer.data['CityId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            cityData = JSONParser().parse(request)
            city = City.objects.get(
                CityId=cityData['CityId'])
            citySerializer = CitySerializer(
                city, data=cityData)
            if citySerializer.is_valid():
                citySerializer.save()
                return JsonResponse(citySerializer.data['CityId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("Invalid payload", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give CityId to get one detail",)
@api_view(['GET','DELETE'])
def CityApiById(request, CityId=""):
    try:
        if request.method == 'GET':
            city = City.objects.get(CityId=CityId)
            citySerializer = CitySerializer(city)
            return JsonResponse(citySerializer.data, safe=False)
        elif request.method == 'DELETE':
            city = City.objects.get(
                CityId=CityId)
            city.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("Invalid payload", safe=False)
    


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StateSerializer)
@swagger_auto_schema(method='PUT', request_body=StateSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all State Details",)
@api_view(['GET','POST','PUT'])
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
        return JsonResponse("Invalid payload", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give StateId to get one detail",)
@api_view(['GET','DELETE'])
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
        return JsonResponse("Invalid payload", safe=False)