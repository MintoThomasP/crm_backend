from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from app_basic.models import Country, Designation, State, UserGroup, UserPermission
from app_basic.serializers import CountrySerializer, DesignationSerializer, StateSerializer, UserGroupSerializer, UserPermissionSerializer
from app_default.views import retry
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=DesignationSerializer,operation_description="NOTE: API for save Designation")
@swagger_auto_schema(method='PUT', request_body=DesignationSerializer,operation_description="NOTE: API for edit Designation")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all Designation",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Designation by DesignationId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for DELETE Designation by DesignationId",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Designation by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def DesignationByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            designation = Designation.objects.filter(CompanyId=CompanyId)
            designationSerializer = DesignationSerializer(designation,many=True)
            return JsonResponse(designationSerializer.data, safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=UserGroupSerializer,operation_description="NOTE: API for save UserGroup")
@swagger_auto_schema(method='PUT', request_body=UserGroupSerializer,operation_description="NOTE: API for edit UserGroup")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all UserGroup",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get UserGroup by UserGroupId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for DELETE UserGroup by UserGroupId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
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
        return JsonResponse("", safe=False)
    
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get UserGroup by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def UserGroupByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            userGroup = UserGroup.objects.filter(CompanyId=CompanyId)
            userGroup_serializer = UserGroupSerializer(userGroup,many=True)
            return JsonResponse(userGroup_serializer.data, safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=CountrySerializer,operation_description="NOTE: API for save Country")
@swagger_auto_schema(method='PUT', request_body=CountrySerializer,operation_description="NOTE: API for edit Country")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all Country",)
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Country by CountryId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for DELETE Country by CountryId",)
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
@swagger_auto_schema(method='POST', request_body=StateSerializer,operation_description="NOTE: API for save State")
@swagger_auto_schema(method='PUT', request_body=StateSerializer,operation_description="NOTE: API for edit State")
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all State Details")
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
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get state by StateId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for DELETE state by StateId",)
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
    


@swagger_auto_schema(method='GET',operation_description="NOTE: APi for Get all State by CountryId",)
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
@swagger_auto_schema(method='POST', request_body=StateSerializer,operation_description="NOTE: API for save UserPermission")
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all UserPermission")
@api_view(['GET','POST'])
@retry(retries=3, delay=2)
def UserPermissionApi(request):
    try:
        if request.method == 'GET':
            userPermission = UserPermission.objects.all()
            userPermission_serializer = UserPermissionSerializer(
                userPermission, many=True)  
            return JsonResponse(userPermission_serializer.data, safe=False)

        elif request.method == 'POST':
            userPermissionData = JSONParser().parse(request)
            userPermissionSerializer = UserPermissionSerializer(
                data=userPermissionData)
            if userPermissionSerializer.is_valid():
                userPermissionSerializer.save()
                return JsonResponse(userPermissionSerializer.data['UserPermissionId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
      
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)
    


    