from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_default.models import Designation, TaskStatus, UserGroup, UserType
from app_default.serializers import DesignationSerializer, TaskStatusSerializer, UserGroupSerializer, UserTypeSerializer
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