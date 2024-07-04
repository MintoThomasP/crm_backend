from itertools import count
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponse
from app_default.models import TaskStatus
from app_default.serializers import TaskStatusSerializer
from app_project.models import Project, ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectSerializer, ProjectTaskSerializer, ProjectTaskTimingSerializer
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.
from django.utils import timezone
import openpyxl
from datetime import datetime, timedelta


from django.db.models import Sum




# @csrf_exempt
# @api_view(['POST'])
# def StaffReportApiByStaffId(request):
#     staffData = JSONParser().parse(request)
#     staff = Staff.objects.get(StaffId=staffData['StaffId'])
#     staffSerializer = StaffSerializer(staff)
#     StaffDetails = staffSerializer.data
#     if staffData['StartDate'] and staffData['EndDate']:
#         start_date = timezone.datetime.strptime(staffData['StartDate'], '%Y-%m-%d').date()
#         end_date = (timezone.datetime.strptime(staffData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#         projectTasks = ProjectTask.objects.filter(TaskAssignedTo=staffData['StaffId'], ScheduledDeadline__range=(start_date, end_date))
    
#     else:
#         projectTasks = ProjectTask.objects.filter(TaskAssignedTo=staffData['StaffId'])
#     projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
#     CompletedPoint = 0
#     TotalNumberofTask = 0
#     project_time = {}  
#     project_points = {}  # Dictionary to store points earned in each project

#     for row in projectTaskSerializer.data:
#         TotalNumberofTask+=1
#         if row['StartDate'] and row['EndDate']:
#             date_format = '%m/%d/%Y, %I:%M:%S %p'
#             start_date = datetime.strptime(row['StartDate'], date_format)
#             end_date = datetime.strptime(row['EndDate'], date_format)
#             duration = float(row['Duration'])
#             duration_min = duration * 60
#             duration_seconds = duration_min * 60
#             total_time_taken_seconds = (end_date - start_date).total_seconds()
#             if total_time_taken_seconds > duration_seconds:
#                 value1 = (total_time_taken_seconds / duration_seconds) * 100
#                 value_percentage = value1 - 100
#                 point = (row['TaskPoint'] * value_percentage) / 100
#                 CompletedPoint += round(row['TaskPoint'] - point)
#             else:
#                 CompletedPoint += row['TaskPoint']

#             if total_time_taken_seconds > duration_seconds:
#                 value1 = (total_time_taken_seconds / duration_seconds) * 100
#                 value_percentage = value1 - 100
#                 point = (row['TaskPoint'] * value_percentage) / 100
#                 earned_points = round(row['TaskPoint'] - point)
#             else:
#                 earned_points = row['TaskPoint']

#             project_id = row['ProjectId']
#             if project_id in project_time:
#                 project_time[project_id] += total_time_taken_seconds
#             else:
#                 project_time[project_id] = total_time_taken_seconds

#             StaffDetails['TotalCompletedPoints'] = CompletedPoint
#             StaffDetails['TotalNumberofTask'] = TotalNumberofTask

#             # Accumulate points earned in each project
#             if project_id in project_points:
#                 project_points[project_id] += earned_points
#             else:
#                 project_points[project_id] = earned_points

#     project_details = []
#     for project_id, points_earned in project_points.items():
#         project = Project.objects.get(ProjectId=project_id)
#         project_details.append({
#             'ProjectId': project_id,
#             'ProjectName': project.ProjectName,
#             'PointsEarned': points_earned,
#             'TimeSpentSeconds': project_time.get(project_id, 0),  # Use get() to handle missing values
#             'TimeSpentHours': project_time.get(project_id, 0) / 3600  # Use get() to handle missing values
#         })

#     StaffDetails['ProjectDetails'] = project_details

#     return JsonResponse(StaffDetails, safe=False)




# @csrf_exempt
# @api_view(['POST'])
# def AllStaffReportApi(request):
#     staffData = JSONParser().parse(request)
#     staff = Staff.objects.all()
#     staffSerializer = StaffSerializer(staff, many=True)
#     StaffDetails = []

#     for col in staffSerializer.data:
#         if staffData['StartDate'] and staffData['EndDate']:
#             start_date = timezone.datetime.strptime(staffData['StartDate'], '%Y-%m-%d').date()
#             end_date = (timezone.datetime.strptime(staffData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#             projectTask = ProjectTask.objects.filter(TaskAssignedTo=col['StaffId'], ScheduledDeadline__range=(start_date, end_date))
    
#         else:
#             projectTask = ProjectTask.objects.filter(TaskAssignedTo=col['StaffId'])
#         projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
#         CompletedPoint = 0
#         TotalNumberofTask = 0
#         project_time = {}  
#         project_points = {}  # Dictionary to store points earned in each project

#         for row in projectTaskSerializer.data:
#             TotalNumberofTask+=1
#             if row['StartDate'] and row['EndDate']:
#                 date_format = '%m/%d/%Y, %I:%M:%S %p'
#                 start_date = datetime.strptime(row['StartDate'], date_format)
#                 end_date = datetime.strptime(row['EndDate'], date_format)
#                 duration = float(row['Duration'])
#                 duration_min = duration * 60
#                 duration_seconds = duration_min * 60
#                 total_time_taken_seconds = (end_date - start_date).total_seconds()
#                 if total_time_taken_seconds > duration_seconds:
#                     value1 = (total_time_taken_seconds / duration_seconds) * 100
#                     value_percentage = value1 - 100
#                     point = (row['TaskPoint'] * value_percentage) / 100
#                     CompletedPoint += round(row['TaskPoint'] - point)
#                 else:
#                     CompletedPoint += row['TaskPoint']

#                 if total_time_taken_seconds > duration_seconds:
#                     value1 = (total_time_taken_seconds / duration_seconds) * 100
#                     value_percentage = value1 - 100
#                     point = (row['TaskPoint'] * value_percentage) / 100
#                     earned_points = round(row['TaskPoint'] - point)
#                 else:
#                     earned_points = row['TaskPoint']

#                 project_id = row['ProjectId']
#                 if project_id in project_time:
#                     project_time[project_id] += total_time_taken_seconds
#                 else:
#                     project_time[project_id] = total_time_taken_seconds

#                 col['TotalCompletedPoints'] = CompletedPoint
#                 col['TotalNumberofTask'] = TotalNumberofTask

#                 # Accumulate points earned in each project
#                 if project_id in project_points:
#                     project_points[project_id] += earned_points
#                 else:
#                     project_points[project_id] = earned_points

#             project_details = []
#             for project_id, points_earned in project_points.items():
#                 project = Project.objects.get(ProjectId=project_id)
#                 project_details.append({
#                     'ProjectId': project_id,
#                     'ProjectName': project.ProjectName,
#                     'PointsEarned': points_earned,
#                     'TimeSpentSeconds': project_time.get(project_id, 0),  # Use get() to handle missing values
#                     'TimeSpentHours': project_time.get(project_id, 0) / 3600  # Use get() to handle missing values
#                 })

#             col['ProjectDetails'] = project_details
#             StaffDetails.append(col)

#     return JsonResponse(StaffDetails, safe=False)





# @csrf_exempt
# @api_view(['POST'])
# def ProjectReportApiByProjectId(request):
#     projectData = JSONParser().parse(request)
#     project = Project.objects.get(ProjectId=projectData['ProjectId'])
#     projectSerializer = ProjectSerializer(project)
#     ProjectDetails = projectSerializer.data
#     projectTask = ProjectTask.objects.filter(ProjectId=projectData['ProjectId'])
#     projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
    
#     staff_ids_set = set()  # Set to store unique staff IDs
#     StaffDetails = []
    
#     for row in projectTaskSerializer.data:
#         staff_objects = Staff.objects.filter(StaffId=row['TaskAssignedTo'])
        
#         for staff_object in staff_objects:
#             staff_id = staff_object.StaffId
#             if staff_id not in staff_ids_set:
#                 staff_ids_set.add(staff_id)
#                 staff_data = StaffSerializer(staff_object).data
#                 StaffDetails.append(staff_data)
    
#     total_staff_count = len(staff_ids_set)
    
#     ProjectDetails['TotalStaffCount'] = total_staff_count
#     ProjectDetails['StaffDetails'] = StaffDetails
    
#     return JsonResponse(ProjectDetails, safe=False)




# @csrf_exempt
# @api_view(['POST'])
# def ProjectReportApiByProjectId(request):
#     projectData = JSONParser().parse(request)
#     project_id = projectData.get('ProjectId')
#     project = Project.objects.get(ProjectId=project_id)
#     projectSerializer = ProjectSerializer(project)
#     ProjectDetails = projectSerializer.data
#     if projectData['StartDate'] and projectData['EndDate']:
#         start_date = timezone.datetime.strptime(projectData['StartDate'], '%Y-%m-%d').date()
#         end_date = (timezone.datetime.strptime(projectData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#         projectTasks = ProjectTask.objects.filter(ProjectId=projectData['ProjectId'], ScheduledDeadline__range=(start_date, end_date))
#     else:
#         projectTasks = ProjectTask.objects.filter(ProjectId=project_id)
#     projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    
#     staff_details = {}
    
#     for task in projectTasks:
#         staff_id = task.TaskAssignedTo
        
#         if staff_id not in staff_details:
#             staff_details[staff_id] = {
#                 'StaffId': staff_id,
#                 'StaffName': '',  
#                 'TotalTimeWorked': 0  
#             }
        
#         staff = Staff.objects.get(StaffId=staff_id)
#         staffSerializer=StaffSerializer(staff)
#         staff_name = staffSerializer.data['StaffName']
#         staff_details[staff_id]['StaffName'] = staff_name
#         date_format = '%m/%d/%Y, %I:%M:%S %p'
#         start_date = datetime.strptime(task.StartDate, date_format)
#         end_date = datetime.strptime(task.EndDate, date_format)
#         duration = end_date - start_date
#         staff_details[staff_id]['TotalTimeWorked'] += duration.total_seconds() / 3600  # Convert to hours
    
#     StaffDetails = list(staff_details.values())
    
#     total_staff_count = len(StaffDetails)
    
#     ProjectDetails['TotalStaffCount'] = total_staff_count
#     ProjectDetails['StaffDetails'] = StaffDetails
    
#     return JsonResponse(ProjectDetails, safe=False)




# @csrf_exempt
# @api_view(['POST'])
# def AllStaffReportApi(request):
#     staffData = JSONParser().parse(request)
#     staff = Staff.objects.all()
#     staffSerializer = StaffSerializer(staff, many=True)
#     StaffDetails = []

#     for col in staffSerializer.data:
#         if staffData['StartDate'] and staffData['EndDate']:
#             start_date = timezone.datetime.strptime(staffData['StartDate'], '%Y-%m-%d').date()
#             end_date = (timezone.datetime.strptime(staffData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#             projectTask = ProjectTask.objects.filter(TaskAssignedTo=col['StaffId'], ScheduledDeadline__range=(start_date, end_date))
#         else:
#             projectTask = ProjectTask.objects.filter(TaskAssignedTo=col['StaffId'])
        
#         projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
#         CompletedPoint = 0
#         TotalNumberofTask = 0
#         due_task_count = 0
#         completed_task_count = 0
#         on_time_completed_task_count = 0

#         for row in projectTaskSerializer.data:
#             TotalNumberofTask += 1
#             if row['StartDate'] and row['EndDate']:
#                 date_format = '%m/%d/%Y, %I:%M:%S %p'
#                 start_date = datetime.strptime(row['StartDate'], date_format)
#                 end_date = datetime.strptime(row['EndDate'], date_format)
#                 duration = float(row['Duration'])
#                 duration_min = duration * 60
#                 duration_seconds = duration_min * 60
#                 total_time_taken_seconds = (end_date - start_date).total_seconds()
#                 if total_time_taken_seconds > duration_seconds:
#                     value1 = (total_time_taken_seconds / duration_seconds) * 100
#                     value_percentage = value1 - 100
#                     point = (row['TaskPoint'] * value_percentage) / 100
#                     CompletedPoint += round(row['TaskPoint'] - point)
#                 else:
#                     CompletedPoint += row['TaskPoint']
#                     on_time_completed_task_count += 1
            
#             if row['Status'] == '1' or row['Status'] == '2':
#                 due_task_count += 1
#             elif row['Status'] == '3' or row['Status'] == '7':
#                 completed_task_count += 1
#             # elif row['Status'] == '8' or row['Status'] == '9':
#             #     on_time_completed_task_count += 1

#         col['TotalCompletedPoints'] = CompletedPoint
#         col['TotalNumberofTask'] = TotalNumberofTask
#         col['DueTaskCount'] = due_task_count
#         col['CompletedTaskCount'] = completed_task_count
#         col['OnTimeCompletedTaskCount'] = on_time_completed_task_count
#         StaffDetails.append(col)

#     return JsonResponse(StaffDetails, safe=False)




# @csrf_exempt
# @api_view(['POST'])
# def StaffReportApiByStaffId(request):
#     staffData = JSONParser().parse(request)
#     staff = Staff.objects.get(StaffId=staffData['StaffId'])
#     staffSerializer = StaffSerializer(staff)
#     StaffDetails = staffSerializer.data

#     # for staff_item in staffSerializer.data:
#     staff_id = staffData['StaffId']
#     staff_projects = []

#     if staffData.get('StartDate') and staffData.get('EndDate'):
#         start_date = timezone.datetime.strptime(staffData['StartDate'], '%Y-%m-%d').date()
#         end_date = (timezone.datetime.strptime(staffData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#         projects = ProjectTask.objects.filter(TaskAssignedTo=staff_id, ScheduledDeadline__range=(start_date, end_date)).values('ProjectId').distinct()
        
#     else:
#         projects = ProjectTask.objects.filter(TaskAssignedTo=staff_id).values('ProjectId').distinct()
#     project_task_serializer = ProjectTaskSerializer(projects, many=True)

#     for task_data in project_task_serializer.data:
#         project_name = task_data['ProjectId']
#         # project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id, ProjectId=project_name)
        
#         project=Project.objects.get(ProjectId=project_name)
#         project_details = {
#             'ProjectId': project_name,
#             'ProjectName':project.ProjectName,
#             'TotalCompletedPoints': 0,
#             'TotalNumberofTask': 0,
#             'DueTaskCount': 0,
#             'CompletedTaskCount': 0,
#             'OnTimeCompletedTaskCount': 0
#         }
        
#         project_details['TotalNumberofTask'] += 1
#         date_formats = [
#             '%m/%d/%Y, %I:%M:%S %p',  
#             '%m/%d/%Y, %I:%M:%S',     
#             '%d/%m/%Y, %I:%M:%S %p',  
#             '%d/%m/%Y, %I:%M:%S'     
#         ]
#         if task_data['StartDate'] and task_data['EndDate']:
#             for date_format in date_formats:
#                 try:
#                     startDate = datetime.strptime(task_data['StartDate'], date_format)
#                     endDate = datetime.strptime(task_data['EndDate'], date_format)
#                     total_time_taken_seconds = (endDate - startDate).total_seconds()
                    
#                 except:
#                     p=""
            
#             try:
#                 duration_parts = task_data['Duration'].split(':')
#                 hours = int(duration_parts[0])*60
#                 minutes = int(duration_parts[1])
#                 duration_min=hours + minutes
#                 duration_seconds=duration_min*60
#             except:
#                 duration_seconds=3600
            
            
#             if total_time_taken_seconds > duration_seconds:
#                 value1 = (total_time_taken_seconds / duration_seconds) * 100
#                 value_percentage = value1 - 100
#                 point = (float(task_data['TaskPoint']) * value_percentage) / 100
#                 project_details['TotalCompletedPoints'] += round(float(task_data['TaskPoint']) - point)
#             else:
#                 project_details['TotalCompletedPoints'] += float(task_data['TaskPoint'])
#                 project_details['OnTimeCompletedTaskCount'] += 1
#         if task_data['Status'] == '1' or task_data['Status'] == '2':
#             project_details['DueTaskCount'] += 1
#         elif task_data['Status'] == '3' or task_data['Status'] == '7':
#             project_details['CompletedTaskCount'] += 1
#     staff_projects.append(project_details)
#     StaffDetails['Projects'] = staff_projects
#     return JsonResponse(StaffDetails, safe=False)


###############
@csrf_exempt
@api_view(['POST'])
def StaffReportApiByStaffId(request):
    staffData = JSONParser().parse(request)
    staff_id = staffData['StaffId']
    start_date = staffData.get('StartDate')
    end_date = staffData.get('EndDate')

    try:
        staff = Staff.objects.get(StaffId=staff_id)
    except:
        return JsonResponse("", status=404)
    
    staffSerializer = StaffSerializer(staff)
    StaffDetails = staffSerializer.data

    if start_date and end_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = (timezone.datetime.strptime(end_date, '%Y-%m-%d') + timezone.timedelta(days=1)).date()
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id, CreatedDate__range=(start_date, end_date))
    else:
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id)

    project_ids = project_tasks.values_list('ProjectId', flat=True).distinct()
    projects = Project.objects.filter(ProjectId__in=project_ids)
   

    # date_formats = [
    #     '%m/%d/%Y, %I:%M:%S %p',  
    #     '%m/%d/%Y, %I:%M:%S',     
    #     '%d/%m/%Y, %I:%M:%S %p',  
    #     '%d/%m/%Y, %I:%M:%S'     
    # ]

    staff_projects = []

    for project in projects:
        project_id = project.ProjectId
        project_details = {
            'ProjectId': project_id,
            'ProjectName': project.ProjectName,
            'TotalCompletedPoints': 0,
            'TotalNumberofTask': 0,
            'DueTaskCount': 0,
            'CompletedTaskCount': 0,
            'OnTimeCompletedTaskCount': 0
        }

        project_tasks_filtered = project_tasks.filter(ProjectId=project_id)

        for task in project_tasks_filtered:
            project_details['TotalNumberofTask'] += 1
            
           
                
            # if task.ScheduledDeadline:
            #     ScheduledDeadline = datetime.strptime(task.ScheduledDeadline, '%Y-%m-%dT%H:%M')
                
            # else:
            #     p=""
                

            try:
                duration_parts = task.Duration.split(':')
                hours = int(duration_parts[0]) * 60
                minutes = int(duration_parts[1])
                duration_min = hours + minutes
                duration_seconds = duration_min * 60
                print("duration_seconds",duration_seconds)
            except:
                duration_seconds = 3600
            try:
                duration_parts = task.TotalDuration.split(':')
                hours = int(duration_parts[0]) * 60
                minutes = int(duration_parts[1])
                duration_min = hours + minutes
                TotalDuration_seconds = duration_min * 60
                print("TotalDuration_seconds",TotalDuration_seconds)
            except:
                TotalDuration_seconds = 3600
            # try:
            #     if TotalDuration_seconds > duration_seconds:
            #         value_percentage = ((TotalDuration_seconds / duration_seconds) * 100) - 100
            #         print("value_percentage/", value_percentage)
            #         point = ((task.TaskPoint) * value_percentage) / 100
            #         print("point",point)
            #         print("=======")
                    
            #         project_details['TotalCompletedPoints'] += round((task.TaskPoint) - point)
            #     else:
            #         project_details['TotalCompletedPoints'] += round((task.TaskPoint))
            #         project_details['OnTimeCompletedTaskCount'] += 1
            # except:
            #     p=""
            try:
                if TotalDuration_seconds > duration_seconds:
                    value_percentage = ((TotalDuration_seconds / duration_seconds) * 100) - 100
                    print("value_percentage:", value_percentage)
                    
                    point = ((task.TaskPoint) * value_percentage) / 100
                    print("point:", point)
                    print("=======")
                    
                    project_details['TotalCompletedPoints'] += round((task.TaskPoint) - point)
                else:
                    project_details['TotalCompletedPoints'] += round(task.TaskPoint)
                    project_details['OnTimeCompletedTaskCount'] += 1
            except:
                p = ""

            if task.Status in ['1', '2']:
                project_details['DueTaskCount'] += 1
            elif task.Status in ['3', '7']:
                project_details['CompletedTaskCount'] += 1

        staff_projects.append(project_details)

    StaffDetails['Projects'] = staff_projects
    return JsonResponse(StaffDetails, safe=False)



# @csrf_exempt
# @api_view(['POST'])
# def ProjectReportApiByProjectId(request):
#     projectData = JSONParser().parse(request)
#     project_id = projectData.get('ProjectId')
#     project = Project.objects.get(ProjectId=project_id)
#     projectSerializer = ProjectSerializer(project)
#     ProjectDetails = projectSerializer.data
#     if projectData['StartDate'] and projectData['EndDate']:
#         start_date = timezone.datetime.strptime(projectData['StartDate'], '%Y-%m-%d').date()
#         end_date = (timezone.datetime.strptime(projectData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#         projectTasks = ProjectTask.objects.filter(ProjectId=projectData['ProjectId'], ScheduledDeadline__range=(start_date, end_date))
#     else:
#         projectTasks = ProjectTask.objects.filter(ProjectId=project_id)
#     projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    
#     staff_details = {}
    
#     for task in projectTasks:
#         staff_id = task.TaskAssignedTo
        
#         if staff_id not in staff_details:
#             staff_details[staff_id] = {
#                 'StaffId': staff_id,
#                 'StaffName': '',  
                
#             }
        
#         staff = Staff.objects.get(StaffId=staff_id)
#         staffSerializer=StaffSerializer(staff)
#         staff_name = staffSerializer.data['StaffName']
#         staff_details[staff_id]['StaffName'] = staff_name
#         date_format = '%m/%d/%Y, %I:%M:%S %p'
#         start_date = datetime.strptime(task.StartDate, date_format)
#         end_date = datetime.strptime(task.EndDate, date_format)
#         duration = end_date - start_date
#         # Convert to hours
    
#     StaffDetails = list(staff_details.values())
    
#     total_staff_count = len(StaffDetails)
    
#     ProjectDetails['TotalStaffCount'] = total_staff_count
#     ProjectDetails['StaffDetails'] = StaffDetails
    
#     return JsonResponse(ProjectDetails, safe=False)

@csrf_exempt
@api_view(['POST'])
def ProjectReportApiByProjectId(request):
    staffData = JSONParser().parse(request)
    project = Project.objects.get(ProjectId=staffData['ProjectId'])
    projectSerializer = ProjectSerializer(project)
    ProjectDetails = projectSerializer.data

    # for staff_item in staffSerializer.data:
    Project_id = staffData['ProjectId']
    staff_projects = []

    if staffData.get('StartDate') and staffData.get('EndDate'):
       
        start_date = timezone.datetime.strptime(staffData['StartDate'], '%Y-%m-%d').date()
        end_date = (timezone.datetime.strptime(staffData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
        projects = ProjectTask.objects.filter(ProjectId=Project_id, ScheduledDeadline__range=(start_date, end_date)).values('TaskAssignedTo').distinct()
    else:
        projects = ProjectTask.objects.filter(ProjectId=Project_id).values('TaskAssignedTo').distinct()

    for project in projects:
        staff_name = project['TaskAssignedTo']
        project_tasks = ProjectTask.objects.filter(ProjectId=Project_id, TaskAssignedTo=staff_name)
        project_task_serializer = ProjectTaskSerializer(project_tasks, many=True)
        staff=Staff.objects.get(StaffId=staff_name)
        Staff_details = {
            'StaffId': staff_name,
           'StaffName': staff.StaffName,
            'TotalCompletedPoints': 0,
            'TotalNumberofTask': 0,
            'DueTaskCount': 0,
            'CompletedTaskCount': 0,
            'OnTimeCompletedTaskCount': 0
        }
        for task_data in project_task_serializer.data:
            Staff_details['TotalNumberofTask'] += 1
            try:
                if task_data['StartDate'] and task_data['EndDate']:
                    try:
                        date_format = '%m/%d/%Y, %I:%M:%S %p' 
                        start_date = datetime.strptime(task_data['StartDate'], date_format)
                        end_date = datetime.strptime(task_data['EndDate'], date_format)
                    except:
                        date_format = '%d/%m/%Y, %I:%M:%S %p'
                        start_date = datetime.strptime(task_data['StartDate'], date_format)
                        end_date = datetime.strptime(task_data['EndDate'], date_format)

                    try:
                        duration_parts = task_data['Duration'].split(':')
                        hours = int(duration_parts[0])*60
                        minutes = int(duration_parts[1])
                        duration_min=hours + minutes
                        duration_seconds=duration_min*60
                    except:
                        duration_seconds=3600
                    total_time_taken_seconds = (end_date - start_date).total_seconds()
                    if total_time_taken_seconds > duration_seconds:
                        value1 = (total_time_taken_seconds / duration_seconds) * 100
                        value_percentage = value1 - 100
                        point = (float(task_data['TaskPoint']) * value_percentage) / 100
                        Staff_details['TotalCompletedPoints'] += round(float(task_data['TaskPoint']) - point)
                    else:
                        Staff_details['TotalCompletedPoints'] += (float(task_data['TaskPoint']))
                        Staff_details['OnTimeCompletedTaskCount'] += 1
            except:
                Staff_details['TotalCompletedPoints'] =0
                Staff_details['OnTimeCompletedTaskCount']=0
            if task_data['Status'] == '1' or task_data['Status'] == '2':
                Staff_details['DueTaskCount'] += 1
            elif task_data['Status'] == '3' or task_data['Status'] == '7':
                Staff_details['CompletedTaskCount'] += 1
        staff_projects.append(Staff_details)
    ProjectDetails['Projects'] = staff_projects
    # StaffDetails.append(staff_item)

    return JsonResponse(ProjectDetails, safe=False)



@csrf_exempt
@api_view(['POST'])
def getAllProjectReport(request):
    staffData = JSONParser().parse(request)
    project = Project.objects.all()
    projectSerializer = ProjectSerializer(project,many=True)
    ProjectDetails =[]

    for staff_item in projectSerializer.data:
        Project_id = staff_item['ProjectId']
        staff_projects = []

        if staffData.get('StartDate') and staffData.get('EndDate'):
            start_date = timezone.datetime.strptime(staffData['StartDate'], '%Y-%m-%d').date()
            end_date = (timezone.datetime.strptime(staffData['EndDate'], '%Y-%m-%d') + timezone.timedelta(days=1)).date()
            projects = ProjectTask.objects.filter(ProjectId=Project_id, ScheduledDeadline__range=(start_date, end_date)).values('TaskAssignedTo').distinct()
        else:
            projects = ProjectTask.objects.filter(ProjectId=Project_id).values('TaskAssignedTo').distinct()

        for project in projects:
            staff_name = project['TaskAssignedTo']
            project_tasks = ProjectTask.objects.filter(ProjectId=Project_id, TaskAssignedTo=staff_name)
            project_task_serializer = ProjectTaskSerializer(project_tasks, many=True)
            staff=Staff.objects.get(StaffId=staff_name)
            Staff_details = {
                'StaffId': staff_name,
            'StaffName': staff.StaffName,
                'TotalCompletedPoints': 0,
                'TotalNumberofTask': 0,
                'DueTaskCount': 0,
                'CompletedTaskCount': 0,
                'OnTimeCompletedTaskCount': 0
            }
            for task_data in project_task_serializer.data:
                Staff_details['TotalNumberofTask'] += 1
                if task_data['StartDate'] and task_data['EndDate']:
                    start_date = datetime.strptime(task_data['StartDate'], '%m/%d/%Y, %I:%M:%S %p')
                    end_date = datetime.strptime(task_data['EndDate'], '%m/%d/%Y, %I:%M:%S %p')
                    duration = float(task_data['Duration'])
                    duration_min = duration * 60
                    duration_seconds = duration_min * 60
                    total_time_taken_seconds = (end_date - start_date).total_seconds()
                    if total_time_taken_seconds > duration_seconds:
                        value1 = (total_time_taken_seconds / duration_seconds) * 100
                        value_percentage = value1 - 100
                        point = (float(task_data['TaskPoint']) * value_percentage) / 100
                        Staff_details['TotalCompletedPoints'] += round(float(task_data['TaskPoint']) - point)
                    else:
                        Staff_details['TotalCompletedPoints'] += float(task_data['TaskPoint'])
                        Staff_details['OnTimeCompletedTaskCount'] += 1
                if task_data['Status'] == '1' or task_data['Status'] == '2':
                    Staff_details['DueTaskCount'] += 1
                elif task_data['Status'] == '3' or task_data['Status'] == '7':
                    Staff_details['CompletedTaskCount'] += 1
            staff_projects.append(Staff_details)
        staff_item['Projects'] = staff_projects
        ProjectDetails.append(staff_item)

    return JsonResponse(ProjectDetails, safe=False)




# @csrf_exempt
# @api_view(['GET'])
# def StaffDailyReport(request,CurrentDate="",StaffId=""):
#     # staffData = JSONParser().parse(request)
#     Created_date = timezone.datetime.strptime(CurrentDate, '%Y-%m-%d').date()

#     projectTask = ProjectTask.objects.filter(CreatedDate=Created_date,TaskAssignedTo=StaffId)
#     projectTaskSerializer=ProjectTaskSerializer(projectTask,many=True)
#     taskData=[]
#     for row in projectTaskSerializer.data:
#         try:
#             if row['StartDate'] and row['EndDate']:
#                 try:
#                     date_format = '%m/%d/%Y, %I:%M:%S %p' 
#                     start_date = datetime.strptime(row['StartDate'], date_format)
#                     end_date = datetime.strptime(row['EndDate'], date_format)
#                 except:
#                     date_format = '%d/%m/%Y, %I:%M:%S %p'
#                     start_date = datetime.strptime(row['StartDate'], date_format)
#                     end_date = datetime.strptime(row['EndDate'], date_format)

#                 try:
#                     duration_parts = row['Duration'].split(':')
#                     hours = int(duration_parts[0])*60
#                     minutes = int(duration_parts[1])
#                     duration_min=hours + minutes
#                     duration_seconds=duration_min*60
#                 except:
#                     duration_seconds=3600
#                 total_time_taken_seconds = (end_date - start_date).total_seconds()
#                 if total_time_taken_seconds > duration_seconds:
#                     value1 = (total_time_taken_seconds / duration_seconds) * 100
#                     value_percentage = value1-100
#                     point=(row['TaskPoint']*value_percentage)/100
#                     row['CompletedPoint'] = round(row['TaskPoint'] - point)
#                 else:
#                     row['CompletedPoint'] = row['TaskPoint']
#         except:
#             row['CompletedPoint']=""                        
#         taskStatus=TaskStatus.objects.get(StatusId=row['Status'])
#         taskStatusSerializer=TaskStatusSerializer(taskStatus)
#         row['StatusName']=taskStatusSerializer.data['Status']
#         try:
#             project = Project.objects.get(ProjectId=row['ProjectId'])
#             projectSerializer = ProjectSerializer(project)
#             row['ProjectName'] = projectSerializer.data['ProjectName']
#         except:
#             row['ProjectName'] = ""
#         try:
#             staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
#             staffSerializer = StaffSerializer(staff)
#             row['StaffName'] = staffSerializer.data['StaffName']
#         except:
#             row['StaffName']=""
#         try:
#             staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
#             staffSerializer = StaffSerializer(staff)
#             row['TaskAssignedBY'] = staffSerializer.data['StaffName']
#         except:
#             row['TaskAssignedBY']=""

       
        
        
        
#         taskData.append(row)
#     exclude_fields = ["SortId", "ProjectTaskId", "ProjectId", "TaskAssignedTo", "TaskAssignedBy","CompletionPoint","VerifiedBy"]
#     column_order = [
#        "StaffName","TaskAssignedBY", "Title", "Description", "Duration",  "CreatedDate", 
#         "ScheduledDeadline", "StartDate", "EndDate", "Status","TaskPoint", 
#         "VerifiedBy", "CompletedPoint", "StatusName", "ProjectName", 
         
#     ]

#     # Create Excel workbook
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active
#     sheet.title = "Staff Daily Report"

#     # Add headers (excluding unwanted fields)
#     headers = [key for key in column_order if key not in exclude_fields]
#     sheet.append(headers)

#     # Add data rows (excluding unwanted fields and in the desired order)
#     for task in taskData:
#         filtered_task = {key: value for key, value in task.items() if key not in exclude_fields}
#         ordered_task = [filtered_task.get(key, "") for key in headers]
#         sheet.append(ordered_task)

#     # Create a response object
#     response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
#     response['Content-Disposition'] = f'attachment; filename=StaffDailyReport_{CurrentDate}.xlsx'

#     # Save workbook to the response
#     workbook.save(response)

#     return response
    




@csrf_exempt
@api_view(['POST'])
def ReportApiBytaskId(request):
    staffData = JSONParser().parse(request)
    ProjectId = staffData['ProjectId']
    start_date = staffData.get('StartDate')
    end_date = staffData.get('EndDate')

    if start_date and end_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = (timezone.datetime.strptime(end_date, '%Y-%m-%d') + timezone.timedelta(days=1)).date()
        project_tasks = ProjectTask.objects.filter(ProjectId=ProjectId, CreatedDate__range=(start_date, end_date))
    else:
        project_tasks = ProjectTask.objects.filter(ProjectId=ProjectId)

    project_details = {
        'TotalCompletedPoints': 0,
        'OnTimeCompletedTaskCount': 0,
        'DueTaskCount': 0,
        'CompletedTaskCount': 0
    }

    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',
        '%m/%d/%Y, %I:%M:%S',
        '%d/%m/%Y, %I:%M:%S %p',
        '%d/%m/%Y, %I:%M:%S'
    ]

    for task in project_tasks:
        projectTaskserializer = ProjectTaskSerializer(task)
        project_data = projectTaskserializer.data

        if task.StartDate and task.EndDate:
            startDate, endDate = None, None
            for date_format in date_formats:
                try:
                    startDate = datetime.strptime(task.StartDate, date_format)
                    endDate = datetime.strptime(task.EndDate, date_format)
                    break
                except ValueError:
                    continue

            if startDate and endDate:
                total_time_taken_seconds = (endDate - startDate).total_seconds()

                duration_seconds = 3600  # Default to 1 hour if duration is invalid
                try:
                    duration_parts = task.Duration.split(':')
                    hours = int(duration_parts[0]) * 60
                    minutes = int(duration_parts[1])
                    duration_min = hours + minutes
                    duration_seconds = duration_min * 60
                except (ValueError, IndexError):
                    pass

                ScheduledDeadline = None
                try:
                    ScheduledDeadline = datetime.strptime(task.ScheduledDeadline, '%Y-%m-%dT%H:%M')
                except (ValueError, TypeError):
                    pass

                try:
                    if ScheduledDeadline and (ScheduledDeadline < endDate or total_time_taken_seconds > duration_seconds):
                        value_percentage = ((total_time_taken_seconds / duration_seconds) * 100) - 100
                        point = ((task.TaskPoint) * value_percentage) / 100
                        project_details['TotalCompletedPoints'] += round((task.TaskPoint) - point)
                        print(task)
                        print(project_details['TotalCompletedPoints'])
                    else:
                        project_details['TotalCompletedPoints'] += round((task.TaskPoint))
                        print(task)
                        print(project_details['TotalCompletedPoints'])
                        project_details['OnTimeCompletedTaskCount'] += 1
                except:
                    pass

            if task.Status in ['1', '2']:
                project_details['DueTaskCount'] += 1
            elif task.Status in ['3', '7']:
                project_details['CompletedTaskCount'] += 1

    return JsonResponse(project_details, safe=False)





import openpyxl
from django.http import HttpResponse
from rest_framework.decorators import api_view
from django.utils import timezone
from PIL import Image as PILImage, ImageDraw, ImageFont
import io
from datetime import datetime

# @csrf_exempt
# @api_view(['GET'])
# def StaffDailyReport(request, CurrentDate="", StaffId=""):
#     Created_date = timezone.datetime.strptime(CurrentDate, '%Y-%m-%d').date()

#     projectTask = ProjectTask.objects.filter(CreatedDate=Created_date, TaskAssignedTo=StaffId)
#     projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
#     taskData = []
#     for row in projectTaskSerializer.data:
#         try:
#             if row['StartDate'] and row['EndDate']:
#                 try:
#                     date_format = '%m/%d/%Y, %I:%M:%S %p'
#                     start_date = datetime.strptime(row['StartDate'], date_format)
#                     end_date = datetime.strptime(row['EndDate'], date_format)
#                 except:
#                     date_format = '%d/%m/%Y, %I:%M:%S %p'
#                     start_date = datetime.strptime(row['StartDate'], date_format)
#                     end_date = datetime.strptime(row['EndDate'], date_format)

#                 try:
#                     duration_parts = row['Duration'].split(':')
#                     hours = int(duration_parts[0]) * 60
#                     minutes = int(duration_parts[1])
#                     duration_min = hours + minutes
#                     duration_seconds = duration_min * 60
#                 except:
#                     duration_seconds = 3600
#                 total_time_taken_seconds = (end_date - start_date).total_seconds()
#                 if total_time_taken_seconds > duration_seconds:
#                     value1 = (total_time_taken_seconds / duration_seconds) * 100
#                     value_percentage = value1 - 100
#                     point = (row['TaskPoint'] * value_percentage) / 100
#                     row['CompletedPoint'] = round(row['TaskPoint'] - point)
#                 else:
#                     row['CompletedPoint'] = row['TaskPoint']
#         except:
#             row['CompletedPoint'] = ""
#         taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
#         taskStatusSerializer = TaskStatusSerializer(taskStatus)
#         row['StatusName'] = taskStatusSerializer.data['Status']
#         try:
#             project = Project.objects.get(ProjectId=row['ProjectId'])
#             projectSerializer = ProjectSerializer(project)
#             row['ProjectName'] = projectSerializer.data['ProjectName']
#         except:
#             row['ProjectName'] = ""
#         try:
#             staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
#             staffSerializer = StaffSerializer(staff)
#             row['StaffName'] = staffSerializer.data['StaffName']
#         except:
#             row['StaffName'] = ""
#         try:
#             staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
#             staffSerializer = StaffSerializer(staff)
#             row['TaskAssignedBY'] = staffSerializer.data['StaffName']
#         except:
#             row['TaskAssignedBY'] = ""
#         taskData.append(row)

#     exclude_fields = ["SortId", "ProjectTaskId", "ProjectId", "TaskAssignedTo","CreatedDate", "Description", "TaskAssignedBy", "CompletionPoint", "VerifiedBy"]
#     column_order = [
#         "StaffName", "TaskAssignedBY","ProjectName", "Title", "Duration", 
#         "ScheduledDeadline", "StartDate", "EndDate", "Status", "TaskPoint",
#         "VerifiedBy", "CompletedPoint", "StatusName", 
#     ]

    
#     workbook = openpyxl.Workbook()
#     sheet = workbook.active
#     sheet.title = "Staff Daily Report"

  
#     headers = [key for key in column_order if key not in exclude_fields]
#     sheet.append(headers)

    
#     for task in taskData:
#         filtered_task = {key: value for key, value in task.items() if key not in exclude_fields}
#         ordered_task = [filtered_task.get(key, "") for key in headers]
#         sheet.append(ordered_task)

   
#     max_col_widths = [len(header) for header in headers]
#     for task in taskData:
#         for i, header in enumerate(headers):
#             max_col_widths[i] = max(max_col_widths[i], len(str(task.get(header, ""))))

   
#     col_width = 12  # approximate width of each character in pixels
#     image_width = sum([w * col_width for w in max_col_widths]) + 20  # extra padding

    
#     img = PILImage.new('RGB', (image_width, 50 * (len(taskData) + 1)), 'white')
#     draw = ImageDraw.Draw(img)
#     font = ImageFont.load_default()

#     row_pos = 10
#     col_pos = 10
#     for col, header in enumerate(headers):
#         draw.text((col_pos, row_pos), header, fill='black', font=font)
#         col_pos += max_col_widths[col] * col_width

#     row_pos += 30
#     for task in taskData:
#         col_pos = 10
#         for col, header in enumerate(headers):
#             draw.text((col_pos, row_pos), str(task.get(header, "")), fill='black', font=font)
#             col_pos += max_col_widths[col] * col_width
#         row_pos += 30

   
#     img_stream = io.BytesIO()
#     img.save(img_stream, format='PNG')
#     img_stream.seek(0)

   
#     response = HttpResponse(img_stream, content_type='image/png')
#     response['Content-Disposition'] = f'attachment; filename=StaffDailyReport_{CurrentDate}.png'

#     return response



@csrf_exempt
@api_view(['GET'])
def StaffDailyReport(request, StaffId=""):
    
    current_date = timezone.now().date()
    
    projectTask = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
    projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
    taskData = []
    
    for row in projectTaskSerializer.data:
        try:
            taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
            taskStatusSerializer = TaskStatusSerializer(taskStatus)
            row['StatusName'] = taskStatusSerializer.data['Status']
        except:
            row['StatusName'] =""

        try:
            project = Project.objects.get(ProjectId=row['ProjectId'])
            projectSerializer = ProjectSerializer(project)
            row['ProjectName'] = projectSerializer.data['ProjectName']
        except:
            row['ProjectName'] = ""
        try:
            staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
            staffSerializer = StaffSerializer(staff)
            row['StaffName'] = staffSerializer.data['StaffName']
        except:
            row['StaffName'] = ""
        try:
            staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
            staffSerializer = StaffSerializer(staff)
            row['TaskAssignedBY'] = staffSerializer.data['StaffName']
        except:
            row['TaskAssignedBY'] = ""
       
        taskTimings = ProjectTaskTiming.objects.filter(ProjectTaskId=row['ProjectTaskId'])
        taskTimingSerializer = ProjectTaskTimingSerializer(taskTimings, many=True)
        
        timing_data = []
        for timing in taskTimingSerializer.data:
            
            start_date = datetime.strptime(timing['StartDate'], '%m/%d/%Y, %I:%M:%S %p').date()
           
            if start_date == current_date:
                timing_data.append(timing)
        if timing_data:
            row['timing'] = timing_data
            taskData.append(row)
    
    
    exclude_fields = ["SortId", "ProjectTaskId", "ProjectId","StartDate", "EndDate", "TaskAssignedTo","CreatedDate", "Description", "TaskAssignedBy", "CompletionPoint", "VerifiedBy"]
    column_order = [
        "StaffName", "TaskAssignedBY","ProjectName", "Title", "Duration", 
        "ScheduledDeadline", "TotalDuration","Status", "TaskPoint",
        "VerifiedBy", "CompletedPoint", "StatusName", 
    ]

    
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Staff Daily Report"

  
    headers = [key for key in column_order if key not in exclude_fields]
    sheet.append(headers)

    
    for task in taskData:
        filtered_task = {key: value for key, value in task.items() if key not in exclude_fields}
        ordered_task = [filtered_task.get(key, "") for key in headers]
        sheet.append(ordered_task)

   
    max_col_widths = [len(header) for header in headers]
    for task in taskData:
        for i, header in enumerate(headers):
            max_col_widths[i] = max(max_col_widths[i], len(str(task.get(header, ""))))

   
    col_width = 12  # approximate width of each character in pixels
    image_width = sum([w * col_width for w in max_col_widths]) + 20  # extra padding

    
    img = PILImage.new('RGB', (image_width, 50 * (len(taskData) + 1)), 'white')
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    row_pos = 10
    col_pos = 10
    for col, header in enumerate(headers):
        draw.text((col_pos, row_pos), header, fill='black', font=font)
        col_pos += max_col_widths[col] * col_width

    row_pos += 30
    for task in taskData:
        col_pos = 10
        for col, header in enumerate(headers):
            draw.text((col_pos, row_pos), str(task.get(header, "")), fill='black', font=font)
            col_pos += max_col_widths[col] * col_width
        row_pos += 30

   
    img_stream = io.BytesIO()
    img.save(img_stream, format='PNG')
    img_stream.seek(0)

   
    response = HttpResponse(img_stream, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename=StaffDailyReport_{current_date}.png'

    return response