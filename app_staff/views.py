from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
import qrcode
from PIL import Image
from io import BytesIO
from app_default.models import Designation
from app_default.serializers import DesignationSerializer
from app_login.serializers import LoginSerializer
from app_staff.models import Staff, StaffGuardian
import os
from app_staff.serializers import SaveStaffSerializer, StaffGuardianSerializer, StaffSerializer, UpdateStaffSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=SaveStaffSerializer)
@swagger_auto_schema(method='PUT', request_body=SaveStaffSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Staff",)
@api_view(['GET','POST','PUT'])
def staffApi(request):
    # try:
        if request.method == 'GET':
           
            staff = Staff.objects.all().order_by('-SortId')
            staffSerializer = StaffSerializer(
                    staff, many=True)
            return JsonResponse(staffSerializer.data, safe=False)
        elif request.method == 'POST':
            staffData = JSONParser().parse(request)
            staffSerializer = SaveStaffSerializer(
                data=staffData)
            if staffSerializer.is_valid():
                staff = staffSerializer.save()

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=9,
                    border=1,
                )
                qr.add_data(f"https://staff.cubexizsoft.in/{staff.StaffCode}")
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                staff.QrCode.save(f'{staff.StaffCode}.png', buffer)
                staff.save()
                loginData={
                    "UserId":staffSerializer.data['StaffId'],
                    "EmailId":staffSerializer.data['EmailId'],
                    "UserType":"db031447-2f11-463b-8582-f49dbe4a634f",
                    "Password":staffSerializer.data['StaffCode']


                }
                loginSerializer=LoginSerializer(data=loginData)
                if loginSerializer.is_valid():
                    loginSerializer.save()


                return JsonResponse(staffSerializer.data['StaffId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            staffData = JSONParser().parse(request)
            staff = Staff.objects.get(
                StaffId=staffData['StaffId'])
            staffSerializer = SaveStaffSerializer(
                staff, data=staffData)
            if staffSerializer.is_valid():
                staffSerializer.save()
                return JsonResponse(staffSerializer.data['StaffId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give StaffId to get one staffdetail",)
@api_view(['GET','DELETE'])
def StaffApiById(request, StaffId=""):
    # try:
        if request.method == 'GET': 
            staff = Staff.objects.get(
                    StaffId=StaffId)
            staffSerializer = StaffSerializer(
                    staff)
            designation=Designation.objects.get(DesignationId=staffSerializer.data['Designation'])
            designationSerializer=DesignationSerializer(designation)
            designationData=staffSerializer.data
            designationData['DesignationName']=designationSerializer.data['Designation']
           
            return JsonResponse(designationData, safe=False)
        elif request.method == 'DELETE':
            staff = Staff.objects.get(StaffId=StaffId)
            staff.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StaffGuardianSerializer)
@swagger_auto_schema(method='PUT', request_body=StaffGuardianSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Staff's guardian details",)
@api_view(['GET','POST','PUT'])
def staffGuardianApi(request):
    # try:
        if request.method == 'GET':
           
            staffGuardian = StaffGuardian.objects.all().order_by('-SortId')
            staffGuardianSerializer = StaffGuardianSerializer(
                    staffGuardian, many=True)
            return JsonResponse(staffGuardianSerializer.data, safe=False)
        elif request.method == 'POST':
            staffGuardianData = JSONParser().parse(request)
            staffGuardianSerializer = StaffGuardianSerializer(
                data=staffGuardianData)
            if staffGuardianSerializer.is_valid():
                staffGuardianSerializer.save()
                return JsonResponse(staffGuardianSerializer.data['StaffGuardianId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            staffGuardianData = JSONParser().parse(request)
            staffGuardian = StaffGuardian.objects.get(
                StaffGuardianId=staffGuardianData['StaffGuardianId'])
            staffGuardianSerializer = StaffGuardianSerializer(
                staffGuardian, data=staffGuardianData)
            if staffGuardianSerializer.is_valid():
                staffGuardianSerializer.save()
                return JsonResponse(staffGuardianSerializer.data['StaffGuardianId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give staffGuardianId to get one Guardian detail",)
@api_view(['GET','DELETE'])
def staffGuardianApiById(request, StaffGuardianId=""):
    try:
        if request.method == 'GET': 
            staffGuardian = StaffGuardian.objects.get(
                    StaffGuardianId=StaffGuardianId)
            staffGuardianSerializer = StaffGuardianSerializer(
                    staffGuardian)
            return JsonResponse(staffGuardianSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staffGuardian = Staff.objects.get(StaffGuardianId=StaffGuardianId)
            staffGuardian.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give staffId to get all guardian details",)
@api_view(['GET'])
def staffGuardianApiByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET': 
            staffGuardian = StaffGuardian.objects.filter(
                    StaffId=StaffId)
            staffGuardianSerializer = StaffGuardianSerializer(
                    staffGuardian,many=True)
            return JsonResponse(staffGuardianSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


class  uploadStaffProfileImage(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, pk="", *args, **kwargs):
        try:
            if not pk:
                file_serializer = UpdateStaffSerializer(
                    data=request.data)
                if file_serializer.is_valid():
                    file_serializer.save()
                    return JsonResponse("ok", safe=False)
                else:
                    return JsonResponse("failed", safe=False)
            else:
                staff = Staff.objects.get(
                    StaffId=pk)
                try:
                    Staff.objects.get(
                        StaffId=pk).ProfilePhoto.delete(save=True)
                except:
                    p=""

                staffSerializer = UpdateStaffSerializer(
                    staff, data=request.data)
                if staffSerializer.is_valid():
                    staffSerializer.save()
                    return JsonResponse("ok", safe=False)
                else:
                    return JsonResponse(pk, safe=False)
        except:
            return JsonResponse("", safe=False)
        



@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give staffId to get all guardian details",)
@api_view(['GET'])
def staffApiByStaffCode(request, StaffCode=""):
    try:
        if request.method == 'GET': 
            staff = Staff.objects.get(
                    StaffCode=StaffCode)
            staffSerializer = StaffSerializer(
                    staff)
            return JsonResponse(staffSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    