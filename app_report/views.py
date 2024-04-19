from itertools import count
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse

from app_project.models import Project, ProjectTask
from app_project.serializers import ProjectSerializer, ProjectTaskSerializer
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.


from datetime import datetime

@csrf_exempt
@api_view(['POST'])
def StaffReportApiByStaffId(request):
    staffData = JSONParser().parse(request)
    staff=Staff.objects.get(StaffId=staffData['StaffId'])
    staffSerializer=StaffSerializer(staff)
    StaffDetails=staffSerializer.data
    projectTask=ProjectTask.objects.filter(TaskAssignedTo=staffData['StaffId'])
    projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
    CompletedPoint=0
    TotalNumberofTask=0
    for row in projectTaskSerializer.data: 
        TotalNumberofTask += 1
        if row['StartDate'] and row['EndDate']:
            date_format = '%m/%d/%Y, %I:%M:%S %p' 
            start_date = datetime.strptime(row['StartDate'], date_format)
            end_date = datetime.strptime(row['EndDate'], date_format)
            duration = float(row['Duration'])
            duration_min=duration*60
            duration_seconds=duration_min*60
            total_time_taken_seconds = (end_date - start_date).total_seconds()
            if total_time_taken_seconds > duration_seconds:
                value1 = (total_time_taken_seconds / duration_seconds) * 100
                value_percentage = value1-100
                point=(row['TaskPoint']*value_percentage)/100
                CompletedPoint += round(row['TaskPoint'] - point)
                print("1",CompletedPoint)
            else:
                CompletedPoint += row['TaskPoint']
                  
    StaffDetails['TotalCompletedPoints']=CompletedPoint
    StaffDetails['TotalNumberofTask']=TotalNumberofTask
    return JsonResponse(StaffDetails,safe=False)


@csrf_exempt
@api_view(['POST'])
def AllStaffReportApi(request):
    try:
        staffData = JSONParser().parse(request)
        staff = Staff.objects.all()
        staffSerializer = StaffSerializer(staff, many=True)
        StaffDetails = []
        
        for col in staffSerializer.data:
            projectTask = ProjectTask.objects.filter(TaskAssignedTo=col['StaffId'])
            projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
            CompletedPoint = 0
            TotalNumberofTask = 0
            
            for row in projectTaskSerializer.data: 
                TotalNumberofTask += 1
                if row['StartDate'] and row['EndDate']:
                    date_format = '%m/%d/%Y, %I:%M:%S %p' 
                    start_date = datetime.strptime(row['StartDate'], date_format)
                    end_date = datetime.strptime(row['EndDate'], date_format)
                    duration = float(row['Duration'])
                    duration_min = duration * 60
                    duration_seconds = duration_min * 60
                    total_time_taken_seconds = (end_date - start_date).total_seconds()
                    
                    if total_time_taken_seconds > duration_seconds:
                        value1 = (total_time_taken_seconds / duration_seconds) * 100
                        value_percentage = value1 - 100
                        point = (row['TaskPoint'] * value_percentage) / 100
                        CompletedPoint += max(round(row['TaskPoint'] - point), 0)
                    else:
                        CompletedPoint += row['TaskPoint']
                        
            col['TotalCompletedPoints'] = CompletedPoint
            col['TotalNumberofTask'] = TotalNumberofTask
            StaffDetails.append(col)
        
        return JsonResponse(StaffDetails, safe=False)
    except:
        return JsonResponse("Invalid", safe=False)




# @csrf_exempt
# @api_view(['POST'])
# def ProjectReportApiByProjectId(request):
#     projectData = JSONParser().parse(request)
#     project=Project.objects.get(ProjectId=projectData['ProjectId'])
#     projectSerializer=ProjectSerializer(project)
#     ProjectDetails=projectSerializer.data
#     projectTask=ProjectTask.objects.filter(ProjectId=projectData['ProjectId'])
#     projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
#     StaffDetails=[]
    # for row in projectTaskSerializer:
        
        
    # return JsonResponse(ProjectDetails, safe=False)


# @csrf_exempt
# @api_view(['POST'])
# def ProjectReportApiByProjectId(request):
#     projectData = JSONParser().parse(request)
#     project = Project.objects.get(ProjectId=projectData['ProjectId'])
#     projectSerializer = ProjectSerializer(project)
#     ProjectDetails = projectSerializer.data
#     projectTask = ProjectTask.objects.filter(ProjectId=projectData['ProjectId'])
#     projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
#     total_staff_count = 0
#     StaffDetails = []
    
#     for row in projectTaskSerializer.data:
#         staff_objects = Staff.objects.filter(StaffId=row['TaskAssignedTo']) 
#         total_staff_count += staff_objects.count()
        
        
#         staff_data = StaffSerializer(staff_objects, many=True).data
#         StaffDetails.extend(staff_data)
    
#     ProjectDetails['TotalStaffCount'] = total_staff_count
#     ProjectDetails['StaffDetails'] = StaffDetails
    
#     return JsonResponse(ProjectDetails, safe=False)
    

@csrf_exempt
@api_view(['POST'])
def ProjectReportApiByProjectId(request):
    projectData = JSONParser().parse(request)
    project = Project.objects.get(ProjectId=projectData['ProjectId'])
    projectSerializer = ProjectSerializer(project)
    ProjectDetails = projectSerializer.data
    projectTask = ProjectTask.objects.filter(ProjectId=projectData['ProjectId'])
    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
    
    staff_ids_set = set()  # Set to store unique staff IDs
    StaffDetails = []
    
    for row in projectTaskSerializer.data:
        staff_objects = Staff.objects.filter(StaffId=row['TaskAssignedTo'])
        
        for staff_object in staff_objects:
            staff_id = staff_object.StaffId
            if staff_id not in staff_ids_set:
                staff_ids_set.add(staff_id)
                staff_data = StaffSerializer(staff_object).data
                StaffDetails.append(staff_data)
    
    total_staff_count = len(staff_ids_set)
    
    ProjectDetails['TotalStaffCount'] = total_staff_count
    ProjectDetails['StaffDetails'] = StaffDetails
    
    return JsonResponse(ProjectDetails, safe=False)