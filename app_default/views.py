from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_default.models import TaskStatus, UserType
from app_default.serializers import TaskStatusSerializer, UserTypeSerializer




@csrf_exempt
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
    