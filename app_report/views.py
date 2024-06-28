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
from django.utils import timezone

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
@csrf_exempt
@api_view(['POST'])
def StaffReportApiByStaffId(request):
    staffData = JSONParser().parse(request)
    staff_id = staffData['StaffId']
    start_date = staffData.get('StartDate')
    end_date = staffData.get('EndDate')

    try:
        staff = Staff.objects.get(StaffId=staff_id)
    except Staff.DoesNotExist:
        return JsonResponse({'error': 'Staff not found'}, status=404)
    
    staffSerializer = StaffSerializer(staff)
    StaffDetails = staffSerializer.data

    if start_date and end_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = (timezone.datetime.strptime(end_date, '%Y-%m-%d') + timezone.timedelta(days=1)).date()
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id, ScheduledDeadline__range=(start_date, end_date))
    else:
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id)

    project_ids = project_tasks.values_list('ProjectId', flat=True).distinct()
    projects = Project.objects.filter(ProjectId__in=project_ids)

    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',  
        '%m/%d/%Y, %I:%M:%S',     
        '%d/%m/%Y, %I:%M:%S %p',  
        '%d/%m/%Y, %I:%M:%S'     
    ]

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

                    try:
                        duration_parts = task.Duration.split(':')
                        hours = int(duration_parts[0]) * 60
                        minutes = int(duration_parts[1])
                        duration_min = hours + minutes
                        duration_seconds = duration_min * 60
                    except:
                        duration_seconds = 3600  # Default to 1 hour if duration is invalid

                    if total_time_taken_seconds > duration_seconds:
                        value1 = (total_time_taken_seconds / duration_seconds) * 100
                        value_percentage = value1 - 100
                        point = (float(task.TaskPoint) * value_percentage) / 100
                        project_details['TotalCompletedPoints'] += round(float(task.TaskPoint) - point)
                    else:
                        project_details['TotalCompletedPoints'] += round(float(task.TaskPoint))
                        project_details['OnTimeCompletedTaskCount'] += 1

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