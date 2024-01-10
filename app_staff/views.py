from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
@csrf_exempt
def staffApi(request):
    try:
        if request.method == 'GET':
           
            staff = Staff.objects.all().order_by('-SortId')
            staffSerializer = StaffSerializer(
                    staff, many=True)
            return JsonResponse(staffSerializer.data, safe=False)
        elif request.method == 'POST':
            staffData = JSONParser().parse(request)
            staffSerializer = StaffSerializer(
                data=staffData)
            if staffSerializer.is_valid():
                staffSerializer.save()
                return JsonResponse(staffSerializer.data['StaffId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            staffData = JSONParser().parse(request)
            staff = Staff.objects.get(
                StaffId=staffData['StaffId'])
            staffSerializer = StaffSerializer(
                staff, data=staffData)
            if staffSerializer.is_valid():
                staffSerializer.save()
                return JsonResponse(staffSerializer.data['StaffId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
def StaffApiById(request, StaffId=""):
    try:
        if request.method == 'GET': 
            staff = Staff.objects.get(
                    StaffId=StaffId)
            staffSerializer = StaffSerializer(
                    staff)
            return JsonResponse(staffSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staff = Staff.objects.get(StaffId=StaffId)
            staff.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)