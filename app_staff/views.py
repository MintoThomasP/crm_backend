from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_project.models import ProjectTask
from app_project.serializers import ProjectTaskSerializer
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
import qrcode
from PIL import Image
from io import BytesIO
from app_default.models import Designation, LeaveStatus, LeaveType
from app_default.serializers import DesignationSerializer, LeaveStatusSerializer, LeaveTypeSerializer
from app_login.serializers import LoginSerializer
from app_staff.models import LeaveApplication, Staff, StaffDocuments, StaffGuardian
import os
from app_staff.serializers import LeaveApplicationSerializer, SaveStaffSerializer, StaffDocumentsSerializer, StaffGuardianSerializer, StaffSerializer, UpdateStaffSerializer, UploadStaffDocumentsSerializer
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
            designationData=[]
            for row in staffSerializer.data:
                designation=Designation.objects.get(DesignationId=row['Designation'])
                designationSerializer=DesignationSerializer(designation)
                row['DesignationName']=designationSerializer.data['Designation']

                projectTask=ProjectTask.objects.filter(TaskAssignedTo=row['StaffId'])
                projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
                work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0, 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
                current_date = str(date.today())
            
                for task in projectTaskSerializer.data:
                    if task['Status'] == '1' or task['Status'] == '2':
                        work_status_count['Pending'] += 1
                
                    if task['Status'] == '3':
                        work_status_count['Completed'] += 1
            
                    if task['CreatedDate'] < current_date and task['Status'] == '1':
                        work_status_count['Due'] += 1

                    if task['Status'] == '8' or task['Status'] == '9':
                        work_status_count['Delay Finished'] += 1

                    if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                        work_status_count['Not Completed'] += 1   

                    if task['Status'] == '7':
                        work_status_count['Finished'] += 1

                row['WorkStatusCount'] = work_status_count
                designationData.append(row)
            
                
            return JsonResponse(designationData, safe=False)
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
from datetime import datetime,date, timedelta   
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

            projectTask=ProjectTask.objects.filter(TaskAssignedTo=staffSerializer.data['StaffId'])
            projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
            work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0, 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
            current_date = str(date.today())
          
            for task in projectTaskSerializer.data:
              
                if task['Status'] == '1' or task['Status'] == '2':
                        work_status_count['Pending'] += 1
                
                if task['Status'] == '3':
                    work_status_count['Completed'] += 1
        
                if task['CreatedDate'] < current_date and task['Status'] == '1':
                    work_status_count['Due'] += 1

                if task['Status'] == '8' or task['Status'] == '9':
                    work_status_count['Delay Finished'] += 1

                if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                    work_status_count['Not Completed'] += 1   

                if task['Status'] == '7':
                    work_status_count['Finished'] += 1

            designationData['WorkStatusCount'] = work_status_count
           
            
           
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
    # try:
        if request.method == 'GET': 
            staffGuardian = StaffGuardian.objects.get(
                    StaffGuardianId=StaffGuardianId)
            staffGuardianSerializer = StaffGuardianSerializer(
                    staffGuardian)
            return JsonResponse(staffGuardianSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staffGuardian = StaffGuardian.objects.get(StaffGuardianId=StaffGuardianId)
            staffGuardian.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    

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
    # try:
        if request.method == 'GET': 
            staff = Staff.objects.get(
                    StaffCode=StaffCode)
            staffSerializer = StaffSerializer(
                    staff)
            StaffData=staffSerializer.data
            try:
                designation=Designation.objects.get(DesignationId=StaffData['Designation'])
                designationSerializer=DesignationSerializer(designation)
                StaffData['DesignationName']=designationSerializer.data['Designation']
            except:
                StaffData['DesignationName']=""
            
            projectTask=ProjectTask.objects.filter(TaskAssignedTo=staffSerializer.data['StaffId'])
            projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
            work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0, 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
            current_date = str(date.today())
          
            for task in projectTaskSerializer.data:
                if task['Status'] == '1' or task['Status'] == '2':
                        work_status_count['Pending'] += 1
                
                if task['Status'] == '3':
                    work_status_count['Completed'] += 1
        
                if task['CreatedDate'] < current_date and task['Status'] == '1':
                    work_status_count['Due'] += 1

                if task['Status'] == '8' or task['Status'] == '9':
                    work_status_count['Delay Finished'] += 1

                if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                    work_status_count['Not Completed'] += 1   

                if task['Status'] == '7':
                    work_status_count['Finished'] += 1

            StaffData['WorkStatusCount'] = work_status_count

            
            return JsonResponse(StaffData, safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StaffDocumentsSerializer)
@swagger_auto_schema(method='PUT', request_body=StaffDocumentsSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Staff's Documents details",)
@api_view(['GET','POST','PUT'])
def staffDocumentsApi(request):
    # try:
        if request.method == 'GET':
           
            staffDocuments = StaffDocuments.objects.all().order_by('-SortId')
            staffDocumentsSerializer = StaffDocumentsSerializer(
                    staffDocuments, many=True)
            return JsonResponse(staffDocumentsSerializer.data, safe=False)
        elif request.method == 'POST':
            staffDocumentsData = JSONParser().parse(request)
            staffDocumentsSerializer = StaffDocumentsSerializer(
                data=staffDocumentsData)
            if staffDocumentsSerializer.is_valid():
                staffDocumentsSerializer.save()
                return JsonResponse(staffDocumentsSerializer.data['StaffDocumentId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            staffDocumentsData = JSONParser().parse(request)
            staffDocuments = StaffDocuments.objects.get(
                StaffDocumentId=staffDocumentsData['StaffDocumentId'])
            staffDocumentsSerializer = StaffDocumentsSerializer(
                staffDocuments, data=staffDocumentsData)
            if staffDocumentsSerializer.is_valid():
                staffDocumentsSerializer.save()
                return JsonResponse(staffDocumentsSerializer.data['StaffDocumentId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give staffDocumentsId to get one Documents detail",)
@api_view(['GET','DELETE'])
def staffDocumentsApiById(request, StaffDocumentId=""):
    # try:
        if request.method == 'GET': 
            staffDocuments = StaffDocuments.objects.get(
                    StaffDocumentId=StaffDocumentId)
            staffDocumentsSerializer = StaffDocumentsSerializer(
                    staffDocuments)
            return JsonResponse(staffDocumentsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staffDocuments = StaffDocuments.objects.get(StaffDocumentId=StaffDocumentId)
            staffDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)
        



class  uploadStaffDocuments(APIView):
    parser_classes = (MultiPartParser, FormParser)
    def post(self, request, StaffDocumentId="", *args, **kwargs):
        try:
            
            staff = StaffDocuments.objects.get(
                StaffDocumentId=StaffDocumentId)
            try:
                StaffDocuments.objects.get(
                    StaffDocumentId=StaffDocumentId).Document.delete(save=True)
            except:
                p=""

            staffSerializer = UploadStaffDocumentsSerializer(
                staff, data=request.data)
            if staffSerializer.is_valid():
                staffSerializer.save()
                return JsonResponse("ok", safe=False)
            else:
                return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)
        


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give staffId to get all StaffDocuments details",)
@api_view(['GET'])
def staffDocumentsApiByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET': 
            staffDocuments = StaffDocuments.objects.filter(
                    StaffId=StaffId)
            staffDocumentsSerializer = StaffDocumentsSerializer(
                    staffDocuments,many=True)
            return JsonResponse(staffDocumentsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    

@csrf_exempt

@swagger_auto_schema(method='GET',operation_description="NOTE: Get all active Staff",)
@api_view(['GET','POST','PUT'])
def GetAllActiveStaffListApi(request):
    try:
        if request.method == 'GET':
           
            staff = Staff.objects.filter(Status=1)
            staffSerializer = StaffSerializer(
                    staff, many=True)
            return JsonResponse(staffSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    


@csrf_exempt
@api_view(['POST'])
def staffSalaryByPerformanceApi(request):
    # try:
        if request.method == 'POST':
            requestData = JSONParser().parse(request)
            month=requestData['Month']
            year=requestData['Year']
            # start_date=1-month-year
            # end_date=31-month-year

            start_date = datetime(year, month, 1)
            end_date = start_date.replace(day=1, month=start_date.month % 12 + 1) - timedelta(days=1)
            
        
            projectTask=ProjectTask.objects.filter(TaskAssignedTo=requestData['StaffId'],ScheduledDeadline__range=(start_date, end_date))
            projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
           
            CompletedPoint=0
            TaskPoint=0
            for row in projectTaskSerializer.data:
                TaskPoint+=row['TaskPoint']
               
                if row['StartDate'] and row['EndDate']:
                    try:
                        date_format = '%m/%d/%Y, %I:%M:%S %p' 
                        start_date = datetime.strptime(row['StartDate'], date_format)
                        end_date = datetime.strptime(row['EndDate'], date_format)
                    except:
                        date_format = '%d/%m/%Y, %I:%M:%S %p'
                        start_date = datetime.strptime(row['StartDate'], date_format)
                        end_date = datetime.strptime(row['EndDate'], date_format)
                    try:
                        duration_parts = row['Duration'].split(':')
                        hours = int(duration_parts[0])*60
                        minutes = int(duration_parts[1])
                        duration_min=hours + minutes
                        duration_seconds=duration_min*60
                    except:
                        duration_seconds=3600

                    total_time_taken_seconds = (end_date - start_date).total_seconds()
                    if total_time_taken_seconds > duration_seconds:
                        value1 = (total_time_taken_seconds / duration_seconds) * 100
                        value_percentage = value1-100
                        point=(row['TaskPoint']*value_percentage)/100
                        
                        CompletedPoint += round(row['TaskPoint'] - point)
                       
                    else:
                        CompletedPoint += row['TaskPoint']
                        staff=Staff.objects.get(StaffId=requestData['StaffId'])
                        staffSerializer=StaffSerializer(staff)
                        Salary=int(staffSerializer.data['Salary'])
                       
                        if CompletedPoint < 0 : 
                            Payment=Salary+((Salary*0.1)*(((CompletedPoint/TaskPoint)*100))/100)
                        elif CompletedPoint > TaskPoint:
                            Payment=Salary+((Salary*0.1)*(((CompletedPoint/TaskPoint)*100)-100)/100)
                        else:
                            Payment=Salary

            return JsonResponse(Payment,safe=False)




@csrf_exempt
@swagger_auto_schema(method='POST', request_body=LeaveApplicationSerializer)
@swagger_auto_schema(method='PUT', request_body=LeaveApplicationSerializer)
@swagger_auto_schema(method='GET',operation_description="NOTE: Get all Staff's Documents details",)
@api_view(['GET','POST','PUT'])
def leaveApplicationApi(request):
    try:
        if request.method == 'GET':
           
            leaveApplication = LeaveApplication.objects.all().order_by('-SortId')
            leaveApplicationSerializer = LeaveApplicationSerializer(
                    leaveApplication, many=True)
            leaveData=[]
            for row in leaveApplicationSerializer.data:
                leaveStatus = LeaveStatus.objects.get(StatusId=row['Status'])
                leaveStatus_serializer = LeaveStatusSerializer(leaveStatus)
                row['StatusName']=leaveStatus_serializer.data['Status']
                leaveType = LeaveType.objects.get(LeaveTypeId=row['LeaveType'])
                leaveType_serializer = LeaveTypeSerializer(leaveType)
                row['LeaveTypeName']=leaveType_serializer.data['LeaveType']
                leaveData.append(row)
            return JsonResponse(leaveData, safe=False)
        elif request.method == 'POST':
            leaveApplicationData = JSONParser().parse(request)
            leaveApplicationSerializer = LeaveApplicationSerializer(
                data=leaveApplicationData)
            if leaveApplicationSerializer.is_valid():
                leaveApplicationSerializer.save()
                return JsonResponse(leaveApplicationSerializer.data['LeaveApplicationId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            leaveApplicationData = JSONParser().parse(request)
            leaveApplication = LeaveApplication.objects.get(
                LeaveApplicationId=leaveApplicationData['LeaveApplicationId'])
            leaveApplicationSerializer = LeaveApplicationSerializer(
                leaveApplication, data=leaveApplicationData)
            if leaveApplicationSerializer.is_valid():
                leaveApplicationSerializer.save()
                return JsonResponse(leaveApplicationSerializer.data['LeaveApplicationId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
    
@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give leaveApplicationId to get one Documents detail",)
@api_view(['GET','DELETE'])
def leaveApplicationApiById(request, LeaveApplicationId=""):
    try:
        if request.method == 'GET': 
            leaveApplication = LeaveApplication.objects.get(
                    LeaveApplicationId=LeaveApplicationId)
            leaveApplicationSerializer = LeaveApplicationSerializer(
                    leaveApplication)
            return JsonResponse(leaveApplicationSerializer.data, safe=False)
        elif request.method == 'DELETE':
            leaveApplication = LeaveApplication.objects.get(LeaveApplicationId=LeaveApplicationId)
            leaveApplication.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
        


@csrf_exempt
@swagger_auto_schema(method='GET',operation_description="NOTE: Give StaffId to get one LeaveApplication",)
@api_view(['GET'])
def leaveApplicationApiByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET': 
            leaveApplication = LeaveApplication.objects.filter(
                    StaffId=StaffId)
            leaveApplicationSerializer = LeaveApplicationSerializer(
                    leaveApplication,many=True)
            leaveData=[]
            for row in leaveApplicationSerializer.data:
                leaveStatus = LeaveStatus.objects.get(StatusId=row['Status'])
                leaveStatus_serializer = LeaveStatusSerializer(leaveStatus)
                row['StatusName']=leaveStatus_serializer.data['Status']
                leaveType = LeaveType.objects.get(LeaveTypeId=row['LeaveType'])
                leaveType_serializer = LeaveTypeSerializer(leaveType)
                row['LeaveTypeName']=leaveType_serializer.data['LeaveType']
                leaveData.append(row)
            return JsonResponse(leaveData, safe=False)
        
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)