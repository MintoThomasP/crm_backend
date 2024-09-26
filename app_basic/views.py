from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view

from app_basic.models import BusinessCategory, Country, Designation, ElementCategory, PermissionSection, ProjectScope, State, TempleteType, Unit, UserGroup, UserPermission, WorkPlace
from app_basic.serializers import BusinessCategorySerializer, CountrySerializer, DesignationSerializer, ElementCategorySerializer, PermissionSectionSerializer, ProjectScopeSerializer, StateSerializer, TempleteTypeSerializer, UnitSerializer, UserGroupSerializer, UserPermissionSerializer, WorkPlaceSerializer
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
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Designation by DesignationId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Designation by DesignationId",)
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
            return JsonResponse("", safe=False)
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
            return JsonResponse("", safe=False)
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
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get UserGroup by UserGroupId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete UserGroup by UserGroupId",)
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
            return JsonResponse("", safe=False)
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
            return JsonResponse("", safe=False)
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
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Country by CountryId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Country by CountryId",)
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
            return JsonResponse("", safe=False)
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
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get state by StateId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete state by StateId",)
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
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all State by CountryId",)
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
            return JsonResponse("", safe=False)
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
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all UserPermission")
@api_view(['GET'])
@retry(retries=3, delay=2)
def UserPermissionbySectionTypeApi(request):
    try:
        if request.method == 'GET':
            permissionSection=PermissionSection.objects.all()
            userPermissionSerializer=PermissionSectionSerializer(permissionSection,many=True)
            permissionData=[]
            for row in userPermissionSerializer.data:
                userPermission = UserPermission.objects.filter(PermissionSectionId=row['PermissionSectionId']).order_by('OrderNo')
                userPermission_serializer = UserPermissionSerializer(
                    userPermission, many=True)
                row['Permissions']=userPermission_serializer.data
                permissionData.append(row)
            return JsonResponse(permissionData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
    

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=TempleteTypeSerializer,operation_description="NOTE: API for save TempleteType")
@swagger_auto_schema(method='PUT', request_body=TempleteTypeSerializer,operation_description="NOTE: API for edit TempleteType")
@swagger_auto_schema(method='GET',operation_description="NOTE: API for Get all TempleteType",)
@api_view(['GET','POST','PUT'])
@retry(retries=3, delay=2)
def TempleteTypeApi(request):
    try:
        if request.method == 'GET':
            templeteType = TempleteType.objects.all()
            templeteType_serializer = TempleteTypeSerializer(
                templeteType, many=True)  
            return JsonResponse(templeteType_serializer.data, safe=False)

        elif request.method == 'POST':
            templeteTypeData = JSONParser().parse(request)
            # return JsonResponse(templeteTypeData, safe=False)
            templeteTypeSerializer = TempleteTypeSerializer(
                data=templeteTypeData)
            if templeteTypeSerializer.is_valid():
                templeteTypeSerializer.save()
                return JsonResponse(templeteTypeSerializer.data['TempleteTypeId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            templeteTypeData = JSONParser().parse(request)
            templeteType = TempleteType.objects.get(
                TempleteTypeId=templeteTypeData['TempleteTypeId'])
            templeteTypeSerializer = TempleteTypeSerializer(
                templeteType, data=templeteTypeData)
            if templeteTypeSerializer.is_valid():
                templeteTypeSerializer.save()
                return JsonResponse(templeteTypeSerializer.data['TempleteTypeId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get TempleteType by TempleteTypeId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete TempleteType by TempleteTypeId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def TempleteTypeApiById(request, TempleteTypeId=""):
    try:
        if request.method == 'GET':
            templeteType = TempleteType.objects.get(TempleteTypeId=TempleteTypeId)
            templeteTypeSerializer = TempleteTypeSerializer(templeteType)
            return JsonResponse(templeteTypeSerializer.data, safe=False)
        elif request.method == 'DELETE':
            templeteType = TempleteType.objects.get(
                TempleteTypeId=TempleteTypeId)
            templeteType.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get TempleteType by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def TempleteTypeByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            templeteType = TempleteType.objects.filter(CompanyId=CompanyId)
            templeteTypeSerializer = TempleteTypeSerializer(templeteType,many=True)
            return JsonResponse(templeteTypeSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)






@csrf_exempt
@swagger_auto_schema(method='POST', request_body=UnitSerializer,operation_description="NOTE: API for save Unit")
@swagger_auto_schema(method='PUT', request_body=UnitSerializer,operation_description="NOTE: API for edit Unit")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def UnitApi(request):
    try:
       

        if request.method == 'POST':
            unitData = JSONParser().parse(request)
            # return JsonResponse(unitData, safe=False)
            unitSerializer = UnitSerializer(
                data=unitData)
            if unitSerializer.is_valid():
                unitSerializer.save()
                return JsonResponse(unitSerializer.data['UnitId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            unitData = JSONParser().parse(request)
            unit = Unit.objects.get(
                UnitId=unitData['UnitId'])
            unitSerializer = UnitSerializer(
                unit, data=unitData)
            if unitSerializer.is_valid():
                unitSerializer.save()
                return JsonResponse(unitSerializer.data['UnitId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Unit by UnitId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete Unit by UnitId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def UnitApiById(request, UnitId=""):
    try:
        if request.method == 'GET':
            unit = Unit.objects.get(UnitId=UnitId)
            unitSerializer = UnitSerializer(unit)
            return JsonResponse(unitSerializer.data, safe=False)
        elif request.method == 'DELETE':
            unit = Unit.objects.get(
                UnitId=UnitId)
            unit.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get Unit by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def UnitByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            unit = Unit.objects.filter(CompanyId=CompanyId)
            unitSerializer = UnitSerializer(unit,many=True)
            return JsonResponse(unitSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=WorkPlaceSerializer,operation_description="NOTE: API for save WorkPlace")
@swagger_auto_schema(method='PUT', request_body=WorkPlaceSerializer,operation_description="NOTE: API for edit WorkPlace")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def WorkPlaceApi(request):
    try:
       

        if request.method == 'POST':
            workPlaceData = JSONParser().parse(request)
            # return JsonResponse(workPlaceData, safe=False)
            workPlaceSerializer = WorkPlaceSerializer(
                data=workPlaceData)
            if workPlaceSerializer.is_valid():
                workPlaceSerializer.save()
                return JsonResponse(workPlaceSerializer.data['WorkPlaceId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            workPlaceData = JSONParser().parse(request)
            workPlace = WorkPlace.objects.get(
                WorkPlaceId=workPlaceData['WorkPlaceId'])
            workPlaceSerializer = WorkPlaceSerializer(
                workPlace, data=workPlaceData)
            if workPlaceSerializer.is_valid():
                workPlaceSerializer.save()
                return JsonResponse(workPlaceSerializer.data['WorkPlaceId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get WorkPlace by WorkPlaceId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete WorkPlace by WorkPlaceId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def WorkPlaceApiById(request, WorkPlaceId=""):
    try:
        if request.method == 'GET':
            workPlace = WorkPlace.objects.get(WorkPlaceId=WorkPlaceId)
            workPlaceSerializer = WorkPlaceSerializer(workPlace)
            return JsonResponse(workPlaceSerializer.data, safe=False)
        elif request.method == 'DELETE':
            workPlace = WorkPlace.objects.get(
                WorkPlaceId=WorkPlaceId)
            workPlace.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get WorkPlace by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def WorkPlaceByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            workPlace = WorkPlace.objects.filter(CompanyId=CompanyId)
            workPlaceSerializer = WorkPlaceSerializer(workPlace,many=True)
            return JsonResponse(workPlaceSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectScopeSerializer,operation_description="NOTE: API for save ProjectScope")
@swagger_auto_schema(method='PUT', request_body=ProjectScopeSerializer,operation_description="NOTE: API for edit ProjectScope")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def ProjectScopeApi(request):
    try:
       

        if request.method == 'POST':
            projectScopeData = JSONParser().parse(request)
            # return JsonResponse(projectScopeData, safe=False)
            projectScopeSerializer = ProjectScopeSerializer(
                data=projectScopeData)
            if projectScopeSerializer.is_valid():
                projectScopeSerializer.save()
                return JsonResponse(projectScopeSerializer.data['ProjectScopeId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectScopeData = JSONParser().parse(request)
            projectScope = ProjectScope.objects.get(
                ProjectScopeId=projectScopeData['ProjectScopeId'])
            projectScopeSerializer = ProjectScopeSerializer(
                projectScope, data=projectScopeData)
            if projectScopeSerializer.is_valid():
                projectScopeSerializer.save()
                return JsonResponse(projectScopeSerializer.data['ProjectScopeId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectScope by ProjectScopeId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ProjectScope by ProjectScopeId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ProjectScopeApiById(request, ProjectScopeId=""):
    try:
        if request.method == 'GET':
            projectScope = ProjectScope.objects.get(ProjectScopeId=ProjectScopeId)
            projectScopeSerializer = ProjectScopeSerializer(projectScope)
            return JsonResponse(projectScopeSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectScope = ProjectScope.objects.get(
                ProjectScopeId=ProjectScopeId)
            projectScope.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ProjectScope by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectScopeByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            projectScope = ProjectScope.objects.filter(CompanyId=CompanyId)
            projectScopeSerializer = ProjectScopeSerializer(projectScope,many=True)
            return JsonResponse(projectScopeSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='POST', request_body=BusinessCategorySerializer,operation_description="NOTE: API for save Unit")
@swagger_auto_schema(method='PUT', request_body=BusinessCategorySerializer,operation_description="NOTE: API for edit Unit")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def BusinessCategoryApi(request):
    try:
       

        if request.method == 'POST':
            businessCategoryData = JSONParser().parse(request)
            # return JsonResponse(businessCategoryData, safe=False)
            businessCategorySerializer = BusinessCategorySerializer(
                data=businessCategoryData)
            if businessCategorySerializer.is_valid():
                businessCategorySerializer.save()
                return JsonResponse(businessCategorySerializer.data['BusinessCategoryId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            businessCategoryData = JSONParser().parse(request)
            businessCategory = BusinessCategory.objects.get(
                BusinessCategoryId=businessCategoryData['BusinessCategoryId'])
            businessCategorySerializer = BusinessCategorySerializer(
                businessCategory, data=businessCategoryData)
            if businessCategorySerializer.is_valid():
                businessCategorySerializer.save()
                return JsonResponse(businessCategorySerializer.data['BusinessCategoryId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get BusinessCategory by BusinessCategoryId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete BusinessCategory by BusinessCategoryId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def BusinessCategoryApiById(request, BusinessCategoryId=""):
    try:
        if request.method == 'GET':
            businessCategory = BusinessCategory.objects.get(BusinessCategoryId=BusinessCategoryId)
            businessCategorySerializer = BusinessCategorySerializer(businessCategory)
            return JsonResponse(businessCategorySerializer.data, safe=False)
        elif request.method == 'DELETE':
            businessCategory = BusinessCategory.objects.get(
                BusinessCategoryId=BusinessCategoryId)
            businessCategory.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get BusinessCategory by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def BusinessCategoryByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            businessCategory = BusinessCategory.objects.filter(CompanyId=CompanyId)
            businessCategorySerializer = BusinessCategorySerializer(businessCategory,many=True)
            return JsonResponse(businessCategorySerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ElementCategorySerializer,operation_description="NOTE: API for save Unit")
@swagger_auto_schema(method='PUT', request_body=ElementCategorySerializer,operation_description="NOTE: API for edit Unit")
@api_view(['POST','PUT'])
@retry(retries=3, delay=2)
def ElementCategoryApi(request):
    try:
       

        if request.method == 'POST':
            elementCategoryData = JSONParser().parse(request)
            # return JsonResponse(elementCategoryData, safe=False)
            elementCategorySerializer = ElementCategorySerializer(
                data=elementCategoryData)
            if elementCategorySerializer.is_valid():
                elementCategorySerializer.save()
                return JsonResponse(elementCategorySerializer.data['ElementCategoryId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            elementCategoryData = JSONParser().parse(request)
            elementCategory = ElementCategory.objects.get(
                ElementCategoryId=elementCategoryData['ElementCategoryId'])
            elementCategorySerializer = ElementCategorySerializer(
                elementCategory, data=elementCategoryData)
            if elementCategorySerializer.is_valid():
                elementCategorySerializer.save()
                return JsonResponse(elementCategorySerializer.data['ElementCategoryId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ElementCategory by ElementCategoryId",)
@swagger_auto_schema(method='DELETE',operation_description="NOTE: API for delete ElementCategory by ElementCategoryId",)
@api_view(['GET','DELETE'])
@retry(retries=3, delay=2)
def ElementCategoryApiById(request, ElementCategoryId=""):
    try:
        if request.method == 'GET':
            elementCategory = ElementCategory.objects.get(ElementCategoryId=ElementCategoryId)
            elementCategorySerializer = ElementCategorySerializer(elementCategory)
            return JsonResponse(elementCategorySerializer.data, safe=False)
        elif request.method == 'DELETE':
            elementCategory = ElementCategory.objects.get(
                ElementCategoryId=ElementCategoryId)
            elementCategory.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: API for get ElementCategory by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ElementCategoryByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            elementCategory = ElementCategory.objects.filter(CompanyId=CompanyId)
            elementCategorySerializer = ElementCategorySerializer(elementCategory,many=True)
            return JsonResponse(elementCategorySerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    