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
from app_default.views import retry
from app_login.models import LoginHistory
from app_login.serializers import LoginHistorySerializer
from app_project.models import Project, ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectSerializer, ProjectTaskSerializer, ProjectTaskTimingSerializer
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.
from django.utils import timezone
import openpyxl
from datetime import datetime, timedelta

from PIL import Image as PILImage, ImageDraw, ImageFont
import io
from django.db.models import Sum


###############
# @csrf_exempt
# @api_view(['POST'])
# def StaffReportApiByStaffId(request):
#     staffData = JSONParser().parse(request)
#     staff_id = staffData['StaffId']
#     start_date = staffData.get('StartDate')
#     end_date = staffData.get('EndDate')

#     try:
#         staff = Staff.objects.get(StaffId=staff_id)
#     except:
#         return JsonResponse("", status=404)
    
#     staffSerializer = StaffSerializer(staff)
#     StaffDetails = staffSerializer.data

#     if start_date and end_date:
#         start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
#         end_date = (timezone.datetime.strptime(end_date, '%Y-%m-%d') + timezone.timedelta(days=1)).date()
#         project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id, CreatedDate__range=(start_date, end_date))
       
#     else:
#         project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id)

#     project_ids = project_tasks.values_list('ProjectId', flat=True).distinct()
#     projects = Project.objects.filter(ProjectId__in=project_ids)
   
#     staff_projects = []

#     for project in projects:
#         project_id = project.ProjectId
#         project_details = {
#             'ProjectId': project_id,
#             'ProjectName': project.ProjectName,
#             'TotalCompletedPoints': 0,
#             'TotalNumberofTask': 0,
#             'DueTaskCount': 0,
#             'CompletedTaskCount': 0,
#             'OnTimeCompletedTaskCount': 0
#         }
#         if start_date and end_date:
#             project_tasks_filtered = project_tasks.filter(ProjectId=project_id,CreatedDate__range=(start_date, end_date))
#             print(project_tasks_filtered)
#         else:
#             project_tasks_filtered = project_tasks.filter(ProjectId=project_id)

#         for task in project_tasks_filtered:
#             project_details['TotalNumberofTask'] += 1
            
           
                
#             # if task.ScheduledDeadline:
#             #     ScheduledDeadline = datetime.strptime(task.ScheduledDeadline, '%Y-%m-%dT%H:%M')
                
#             # else:
#             #     p=""
                
#             # duration_seconds=3600
#             if task.TotalDuration:
#                 try:
#                     print("___start____")
#                     print(task.Duration)
#                     duration_parts = task.Duration.split(':')
#                     hours = int(duration_parts[0]) * 60
#                     minutes = int(duration_parts[1])
#                     duration_min = hours + minutes
#                     duration_seconds = duration_min * 60
#                     print("duration_seconds",duration_seconds)
#                 except:
                
#                     duration_seconds = 3600
#                 try:
#                     duration_parts = task.TotalDuration.split(':')
#                     hours = int(duration_parts[0]) * 60
#                     minutes = int(duration_parts[1])
#                     duration_min = hours + minutes
#                     TotalDuration_seconds = duration_min * 60
#                     print("TotalDuration_seconds",TotalDuration_seconds)
#                 except:
#                     TotalDuration_seconds = 3600
#                 try:
#                     if TotalDuration_seconds > duration_seconds:
#                         value_percentage = ((TotalDuration_seconds / duration_seconds) * 100) - 100
#                         print("value_percentage/", value_percentage)
#                         point = ((task.TaskPoint) * value_percentage) / 100
#                         print("point",point)
#                         print("=======")
                        
#                         project_details['TotalCompletedPoints'] += round((task.TaskPoint) - point)
#                     else:
#                         project_details['TotalCompletedPoints'] += round((task.TaskPoint))
#                         project_details['OnTimeCompletedTaskCount'] += 1
#                 except:
#                     p=""
#                 try:
#                     if TotalDuration_seconds > duration_seconds:
#                         print("td inside",TotalDuration_seconds)
#                         print(duration_seconds)
#                         value_percentage = ((TotalDuration_seconds / duration_seconds) * 100) - 100
#                         div=TotalDuration_seconds / duration_seconds
#                         print("t/d",div)
#                         div2=div*100
#                         print("div2",div2)
#                         div3=div2-100
#                         print("div3",div3)
#                         print("value_percentage:", value_percentage)
                        
#                         point = ((task.TaskPoint) * value_percentage) / 100
#                         print("point:", point)
#                         print("=======")
#                         # compPoint=round((task.TaskPoint) - point)
#                         # print(compPoint)
#                         print("tp",project_details['TotalCompletedPoints'])
                        
#                         project_details['TotalCompletedPoints'] += ((task.TaskPoint) - point)
#                         print("tp",project_details['TotalCompletedPoints'])
#                         print("____________End___________")
#                     else:
#                         project_details['TotalCompletedPoints'] += (task.TaskPoint)
#                         project_details['OnTimeCompletedTaskCount'] += 1
#                 except:
#                     p = ""

#             if task.Status in ['1', '2']:
#                 project_details['DueTaskCount'] += 1
#             elif task.Status in ['3', '7']:
#                 project_details['CompletedTaskCount'] += 1

#         staff_projects.append(project_details)

#     StaffDetails['Projects'] = staff_projects
#     return JsonResponse(StaffDetails, safe=False)



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
@retry(retries=3, delay=2)
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
                # if task_data['StartDate'] and task_data['EndDate']:
                #     try:
                #         date_format = '%m/%d/%Y, %I:%M:%S %p' 
                #         start_date = datetime.strptime(task_data['StartDate'], date_format)
                #         end_date = datetime.strptime(task_data['EndDate'], date_format)
                #     except:
                #         date_format = '%d/%m/%Y, %I:%M:%S %p'
                #         start_date = datetime.strptime(task_data['StartDate'], date_format)
                #         end_date = datetime.strptime(task_data['EndDate'], date_format)
                if task_data['TotalDuration']:
                    Duration = task_data['Duration']
                    duration_seconds=durationCalculation(Duration)
                    TotalDuration = task_data['TotalDuration']
                    TotalDuration_seconds=durationCalculation(TotalDuration)
                    point = task_data['TaskPoint']
                    point = pointCalculation(duration_seconds, TotalDuration_seconds, point)

                    Staff_details['TotalCompletedPoints'] += round((task_data['TaskPoint']) - point, 2)
                    if TotalDuration_seconds < duration_seconds:
                        Staff_details['OnTimeCompletedTaskCount'] += 1

                    # try:
                    #     duration_parts = task_data['Duration'].split(':')
                    #     hours = int(duration_parts[0])*60
                    #     minutes = int(duration_parts[1])
                    #     duration_min=hours + minutes
                    #     duration_seconds=duration_min*60
                    # except:
                    #     duration_seconds=3600
                    # total_time_taken_seconds = (end_date - start_date).total_seconds()
                    # if total_time_taken_seconds > duration_seconds:
                    #     value1 = (total_time_taken_seconds / duration_seconds) * 100
                    #     value_percentage = value1 - 100
                    #     point = (float(task_data['TaskPoint']) * value_percentage) / 100
                    #     Staff_details['TotalCompletedPoints'] += round(float(task_data['TaskPoint']) - point)
                    # else:
                    #     Staff_details['TotalCompletedPoints'] += (float(task_data['TaskPoint']))
                    #     Staff_details['OnTimeCompletedTaskCount'] += 1
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
@retry(retries=3, delay=2)
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
                    if task_data['TotalDuration']:
                        Duration = task_data['Duration']
                        duration_seconds=durationCalculation(Duration)
                        TotalDuration = task_data['TotalDuration']
                        TotalDuration_seconds=durationCalculation(TotalDuration)
                        point = task_data['TaskPoint']
                        point = pointCalculation(duration_seconds, TotalDuration_seconds, point)
                        Staff_details['CompletedPoint'] += round((task_data['TaskPoint']) - point, 2)
                        if TotalDuration_seconds < duration_seconds:
                            Staff_details['OnTimeCompletedTaskCount'] += 1

                    # duration = float(task_data['Duration'])
                    # duration_min = duration * 60
                    # duration_seconds = duration_min * 60
                    # total_time_taken_seconds = (end_date - start_date).total_seconds()
                    # if total_time_taken_seconds > duration_seconds:
                    #     value1 = (total_time_taken_seconds / duration_seconds) * 100
                    #     value_percentage = value1 - 100
                    #     point = (float(task_data['TaskPoint']) * value_percentage) / 100
                    #     Staff_details['TotalCompletedPoints'] += round(float(task_data['TaskPoint']) - point)
                    # else:
                    #     Staff_details['TotalCompletedPoints'] += float(task_data['TaskPoint'])
                    #     Staff_details['OnTimeCompletedTaskCount'] += 1
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
# def StaffDailyReport(request, StaffId=""):
    
#     current_date = timezone.now().date()
    
#     projectTask = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
#     projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
#     taskData = []
#     serial_number = 1
#     for row in projectTaskSerializer.data:
#         try:
#             taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
#             taskStatusSerializer = TaskStatusSerializer(taskStatus)
#             row['StatusName'] = taskStatusSerializer.data['Status']
#         except:
#             row['StatusName'] =""

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
#             loginHistory=LoginHistory.objects.get(UserId=StaffId,LoginTime=current_date)
#             loginHistorySerializer=LoginHistorySerializer(loginHistory)
#             row['LoginDetails']=loginHistorySerializer.data
#         except:
#             row['LoginDetails']=""
        
       
#         taskTimings = ProjectTaskTiming.objects.filter(ProjectTaskId=row['ProjectTaskId'])
#         taskTimingSerializer = ProjectTaskTimingSerializer(taskTimings, many=True)
        
#         timing_data = []
#         for timing in taskTimingSerializer.data:
            
#             start_date = datetime.strptime(timing['StartDate'], '%m/%d/%Y, %I:%M:%S %p').date()
           
#             if start_date == current_date:
#                 timing_data.append(timing)
#         if timing_data:
#             row['timing'] = timing_data
#             row['SerialNumber'] = serial_number  # Add serial number to the row
#             serial_number += 1
#             taskData.append(row)
    
    
#     exclude_fields = ["SortId", "ProjectTaskId", "ProjectId","StartDate", "EndDate", "TaskAssignedTo","CreatedDate", "Description",  "CompletionPoint", "VerifiedBy"]
#     column_order = ["SerialNumber",
#         "StaffName","TaskType", "ProjectName", "Title", "TotalDuration", "StatusName", ]

    
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
#     response['Content-Disposition'] = f'attachment; filename=StaffDailyReport_{current_date}.png'

#     return response


##############******##############
# from openpyxl.styles import Border, Side
# @csrf_exempt
# @api_view(['GET'])
# def StaffDailyReport(request, StaffId=""):
#     # try:
#         current_date = timezone.now().date()
#         staff = Staff.objects.get(StaffId=StaffId)
#         StaffName = staff.StaffName
        

#         projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
#         projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
#         taskData = []
#         serial_number = 1
#         date_formats = [
#             '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
#             '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
#             '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
#             '%d/%m/%Y, %H:%M:%S'      # Example: 07/04/2024, 10:06:38
#         ]

#         for row in projectTaskSerializer.data:
#             try:
#                 taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
#                 taskStatusSerializer = TaskStatusSerializer(taskStatus)
#                 row['StatusName'] = taskStatusSerializer.data['Status']
#             except TaskStatus.DoesNotExist:
#                 row['StatusName'] = ""

#             try:
#                 project = Project.objects.get(ProjectId=row['ProjectId'])
#                 projectSerializer = ProjectSerializer(project)
#                 row['ProjectName'] = projectSerializer.data['ProjectName']
#             except Project.DoesNotExist:
#                 row['ProjectName'] = ""

#             try:
#                 assigned_staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
#                 staffSerializer = StaffSerializer(assigned_staff)
#                 row['StaffName'] = staffSerializer.data['StaffName']
#             except Staff.DoesNotExist:
#                 row['StaffName'] = ""

#             try:
#                 login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('-SortId')
                
#                 login_time = ""
#                 logout_time = ""
#                 first_login = False

#                 for login_history in login_histories:
#                     login_time_dt = None
#                     for date_format in date_formats:
#                         try:
#                             login_time_dt = datetime.strptime(login_history.LoginTime, date_format)
#                             if login_time_dt and login_time_dt.date() == current_date:
#                                 login_time = login_history.LoginTime
#                                 logout_time = login_history.LogoutTime if login_history.LogoutTime else ""
#                                 loginHistorySerializer = LoginHistorySerializer(login_history)
#                                 row['LoginDetails'] = loginHistorySerializer.data
#                                 first_login = True
#                                 break

#                         except:
#                             continue

                    

#                 if not first_login:

#                     row['LoginDetails'] = ""
#             except LoginHistory.DoesNotExist:
#                 row['LoginDetails'] = ""

#             taskTimings = ProjectTaskTiming.objects.filter(ProjectTaskId=row['ProjectTaskId'])
#             taskTimingSerializer = ProjectTaskTimingSerializer(taskTimings, many=True)

#             timing_data = []
#             for timing in taskTimingSerializer.data:
#                 start_date = None
#                 for date_format in date_formats:
#                     try:
#                         start_date = datetime.strptime(timing['StartDate'], date_format)
#                         break
#                     except:
#                         continue

#                 if start_date and start_date.date() == current_date:
#                     timing_data.append(timing)

#             if timing_data:
#                 row['timing'] = timing_data
#                 row['SlNo'] = serial_number  # Add serial number to the row
#                 serial_number += 1
#                 taskData.append(row)
#         rename_mapping = {
#                 "SlNo": "SlNo",
#                 "TaskType": "Task Type",
#                 "ProjectName": "Project",
#                 "Title": "Task",
#                 "TotalDuration": "Duration",
#                 "StatusName": "Status"
#             }

#         exclude_fields = ["SortId", "ProjectTaskId", "ProjectId", "StartDate", "EndDate", "StaffName", "TaskAssignedTo", "CreatedDate", "Description", "CompletionPoint", "VerifiedBy"]
#         column_order = ["SlNo", "TaskType", "ProjectName", "Title", "TotalDuration", "StatusName"]

#         workbook = openpyxl.Workbook()
#         sheet = workbook.active
#         sheet.title = "Staff Daily Report"

#         # Apply renaming using the mapping
#         headers = [rename_mapping[key] for key in column_order if key not in exclude_fields]
#         sheet.append(headers)

#         # Define border style
#         thin_border = Border(
#             left=Side(style='thin'),
#             right=Side(style='thin'),
#             top=Side(style='thin'),
#             bottom=Side(style='thin')
#         )

#         # Append headers with borders
#         for col_num, header in enumerate(headers, 1):
#             cell = sheet.cell(row=1, column=col_num)
#             cell.value = header
#             cell.border = thin_border

#         # Append task data with borders
#         for row_num, task in enumerate(taskData, start=2):
#             filtered_task = {key: value for key, value in task.items() if key not in exclude_fields}
#             ordered_task = [filtered_task.get(key, "") for key in column_order if key not in exclude_fields]
#             for col_num, value in enumerate(ordered_task, 1):
#                 cell = sheet.cell(row=row_num, column=col_num)
#                 cell.value = value
#                 cell.border = thin_border

#         # Calculate maximum column widths
#         max_col_widths = [len(header) for header in headers]
#         for task in taskData:
#             for i, key in enumerate(column_order):
#                 if key not in exclude_fields:
#                     max_col_widths[i] = max(max_col_widths[i], len(str(task.get(key, ""))))

#         col_width = 12
#         image_width = sum([w * col_width for w in max_col_widths]) + 20  # extra padding

#         img = PILImage.new('RGB', (image_width, 50 * (len(taskData) + 3)), 'white')
#         draw = ImageDraw.Draw(img)
#         font = ImageFont.load_default()

#         row_pos = 10
#         col_pos = 10

#         # Draw login details
#         login_details = f"Login Time: {login_time},             Logout Time: {logout_time}"
#         draw.text((col_pos, row_pos), login_details, fill='black', font=font)
#         row_pos += 30  # space for next row

#         # Draw headers with borders
#         for col, header in enumerate(headers):
#             draw.text((col_pos, row_pos), header, fill='black', font=font)
#             draw.rectangle([col_pos - 2, row_pos - 2, col_pos + max_col_widths[col] * col_width + 2, row_pos + 12], outline='black')
#             col_pos += max_col_widths[col] * col_width

#         row_pos += 30  # space for next row

#         # Draw task data with borders
#         for task in taskData:
#             col_pos = 10
#             for col, key in enumerate(column_order):
#                 if key not in exclude_fields:
#                     value = str(task.get(key, ""))
#                     draw.text((col_pos, row_pos), value, fill='black', font=font)
#                     draw.rectangle([col_pos - 2, row_pos - 2, col_pos + max_col_widths[col] * col_width + 2, row_pos + 12], outline='black')
#                     col_pos += max_col_widths[col] * col_width
#             row_pos += 30

#         img_stream = io.BytesIO()
#         img.save(img_stream, format='PNG')
#         img_stream.seek(0)

#         response = HttpResponse(img_stream, content_type='image/png')
#         response['Content-Disposition'] = f'attachment; filename={StaffName}DailyReport_{current_date}.png'

#         return response

#         # return JsonResponse(taskData, safe=False)
#         rename_mapping = {
#     "SlNo": "SlNo",
#     "TaskType": "Task Type",
#     "ProjectName": "Project",
#     "Title": "Task",
#     "TotalDuration": "Duration",
#     "StatusName": "Status"
# }
    
#         exclude_fields = ["SortId", "ProjectTaskId", "ProjectId","StartDate", "EndDate","StaffName" "TaskAssignedTo","CreatedDate", "Description",  "CompletionPoint", "VerifiedBy"]
#         column_order = ["SlNo", "TaskType", "ProjectName", "Title", "TotalDuration", "StatusName"]

#         workbook = openpyxl.Workbook()
#         sheet = workbook.active
#         sheet.title = "Staff Daily Report"
        
#         headers = [rename_mapping[key] for key in column_order if key not in exclude_fields]
#         sheet.append(headers)
        
#         for task in taskData:
#             filtered_task = {key: value for key, value in task.items() if key not in exclude_fields}
#             ordered_task = [filtered_task.get(key, "") for key in headers]
#             sheet.append(ordered_task)
        
#         max_col_widths = [len(header) for header in headers]
#         for task in taskData:
#             for i, header in enumerate(headers):
#                 max_col_widths[i] = max(max_col_widths[i], len(str(task.get(header, ""))))
        
#         col_width = 12  
#         image_width = sum([w * col_width for w in max_col_widths]) + 20  # extra padding
        
#         img = PILImage.new('RGB', (image_width, 50 * (len(taskData) + 3)), 'white') 
#         draw = ImageDraw.Draw(img)
#         font = ImageFont.load_default()
        
#         row_pos = 10
#         col_pos = 10
        
#         # Draw login details
#         login_details = f"Login Time: {login_time},             Logout Time: {logout_time}"
#         draw.text((col_pos, row_pos), login_details, fill='black', font=font)
#         row_pos += 30  # space for next row
        
#         # Draw headers
#         for col, header in enumerate(headers):
#             draw.text((col_pos, row_pos), header, fill='black', font=font)
#             col_pos += max_col_widths[col] * col_width
        
#         row_pos += 30  # space for next row
#         for task in taskData:
#             col_pos = 10
#             for col, header in enumerate(headers):
#                 draw.text((col_pos, row_pos), str(task.get(header, "")), fill='black', font=font)
#                 col_pos += max_col_widths[col] * col_width
#             row_pos += 30
        
#         img_stream = io.BytesIO()
#         img.save(img_stream, format='PNG')
#         img_stream.seek(0)
        
#         response = HttpResponse(img_stream, content_type='image/png')
#         response['Content-Disposition'] = f'attachment; filename={StaffName}DailyReport_{current_date}.png'
        
#         return response


@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def StaffReportApiByStaffId(request):
    staffData = JSONParser().parse(request)
    staff_id = staffData['StaffId']
    start_date = staffData.get('StartDate')
    end_date = staffData.get('EndDate')
    try:
        staff = Staff.objects.get(StaffId=staff_id)
        staffSerializer = StaffSerializer(staff)
        StaffDetails = staffSerializer.data
    except:
        p=""
    if start_date and end_date:
        start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = (timezone.datetime.strptime(end_date, '%Y-%m-%d') + timezone.timedelta(days=1)).date()
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id, CreatedDate__range=(start_date, end_date))
    else:
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id)
        
    project_ids = project_tasks.values_list('ProjectId', flat=True).distinct()
    projects = Project.objects.filter(ProjectId__in=project_ids)
    staff_projects = []
    for project in projects:
        project_details = {
            'ProjectId': project.ProjectId,
            'ProjectName': project.ProjectName,
            'TotalCompletedPoints': 0,
            'TotalNumberofTask': 0,
            'DueTaskCount': 0,
            'CompletedTaskCount': 0,
            'OnTimeCompletedTaskCount': 0
        }
        if start_date and end_date:
            project_tasks_filtered = project_tasks.filter(ProjectId=project.ProjectId,CreatedDate__range=(start_date, end_date))
        else:
            project_tasks_filtered = project_tasks.filter(ProjectId=project.ProjectId)
           
        for task in project_tasks_filtered:
            project_details['TotalNumberofTask'] += 1
            if task.Status in ['1', '2']:
                project_details['DueTaskCount'] += 1
            elif task.Status in ['3', '7']:
                project_details['CompletedTaskCount'] += 1
            # if task.TotalDuration:
                # try:
                #     duration_parts = task.Duration.split(':')
                #     hours = int(duration_parts[0]) * 60
                #     minutes = int(duration_parts[1])
                #     duration_min = hours + minutes
                #     duration_seconds = duration_min * 60
                # except:
                #     duration_seconds=3600

                # totalduration_parts = task.TotalDuration.split(':')
                # hours = int(totalduration_parts[0]) * 60
                # minutes = int(totalduration_parts[1])
                # duration_min = hours + minutes
                # TotalDuration_seconds = duration_min * 60
                # if TotalDuration_seconds > duration_seconds:
                #     value_percentage = ((TotalDuration_seconds / duration_seconds) * 100) - 100
                #     point = ((task.TaskPoint) * value_percentage) / 100
                    # Duration=task.Duration
                    # TotalDuration=task.TotalDuration
                    # TaskPoint=task.TaskPoint
                    # point=pointCalculation(Duration,TotalDuration,TaskPoint)
                    # project_details['TotalCompletedPoints'] += round((task.TaskPoint) - point,2)
                # else:
                #     project_details['TotalCompletedPoints'] += round((task.TaskPoint),2)
                    # project_details['OnTimeCompletedTaskCount'] += 1
            if task.TotalDuration:
                Duration = task.Duration
                duration_seconds=durationCalculation(Duration)
                TotalDuration = task.TotalDuration
                TotalDuration_seconds=durationCalculation(TotalDuration)
                point = task.TaskPoint
                point = pointCalculation(duration_seconds, TotalDuration_seconds, point)
                project_details['TotalCompletedPoints'] += round((task.TaskPoint) - point, 2)
                if TotalDuration_seconds < duration_seconds:
                    project_details['OnTimeCompletedTaskCount'] += 1





        staff_projects.append(project_details)

    StaffDetails['Projects'] = staff_projects
    return JsonResponse(StaffDetails, safe=False)

def durationCalculation(Duration=""):
    try:
        duration_parts = Duration.split(':')
        hours = int(duration_parts[0]) * 60
        minutes = int(duration_parts[1])
        duration_min = hours + minutes
        duration_seconds = duration_min * 60
    except Exception as e:
      
        duration_seconds = 3600
    return duration_seconds


def pointCalculation(duration_seconds="", TotalDuration_seconds="", point=""):
    
    value_percentage = ((TotalDuration_seconds / duration_seconds) * 100) - 100
   
    try:
        point = ((point) * value_percentage) / 100
    except:
        point = ((1) * value_percentage) / 100
    
    return point



# from datetime import datetime
# import io
# from django.http import HttpResponse
# from django.utils import timezone
# from rest_framework.decorators import api_view
# from PIL import Image as PILImage, ImageDraw, ImageFont
# from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
# @api_view(['GET'])
# def StaffDailyReport(request, StaffId=""):
#     current_date = timezone.now().date()
#     staff = Staff.objects.get(StaffId=StaffId)
#     StaffName = staff.StaffName

#     projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
#     projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
#     taskData = []
#     serial_number = 1
#     date_formats = [
#         '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
#         '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
#         '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
#         '%d/%m/%Y, %H:%M:%S'      # Example: 07/04/2024, 10:06:38
#     ]

#     for row in projectTaskSerializer.data:
#         try:
#             taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
#             taskStatusSerializer = TaskStatusSerializer(taskStatus)
#             row['StatusName'] = taskStatusSerializer.data['Status']
#         except TaskStatus.DoesNotExist:
#             row['StatusName'] = ""

#         try:
#             project = Project.objects.get(ProjectId=row['ProjectId'])
#             projectSerializer = ProjectSerializer(project)
#             row['ProjectName'] = projectSerializer.data['ProjectName']
#         except Project.DoesNotExist:
#             row['ProjectName'] = ""

#         try:
#             assigned_staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
#             staffSerializer = StaffSerializer(assigned_staff)
#             row['StaffName'] = staffSerializer.data['StaffName']
#         except Staff.DoesNotExist:
#             row['StaffName'] = ""

#         try:
#             login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('SortId')
            
#             login_details = []
#             for login_history in login_histories:
#                 login_time = ""
#                 logout_time = ""

#                 for date_format in date_formats:
#                     try:
#                         login_time_dt = datetime.strptime(login_history.LoginTime, date_format)
#                         if login_time_dt and login_time_dt.date() == current_date:
#                             login_time = login_history.LoginTime
#                             logout_time = login_history.LogoutTime if login_history.LogoutTime else ""
#                             login_details.append(f"Login Time: {login_time},         Logout Time: {logout_time}\n")
#                     except:
#                         continue

           
#         except LoginHistory.DoesNotExist:
#             pass

#         taskTimings = ProjectTaskTiming.objects.filter(ProjectTaskId=row['ProjectTaskId'])
#         taskTimingSerializer = ProjectTaskTimingSerializer(taskTimings, many=True)

#         timing_data = []
#         for timing in taskTimingSerializer.data:
#             start_date = None
#             for date_format in date_formats:
#                 try:
#                     start_date = datetime.strptime(timing['StartDate'], date_format)
#                     break
#                 except:
#                     continue

#             if start_date and start_date.date() == current_date:
#                 timing_data.append(timing)

#         if timing_data:
#             row['timing'] = timing_data
#             row['SlNo'] = serial_number  # Add serial number to the row
#             serial_number += 1
#             taskData.append(row)

#     rename_mapping = {
#         "SlNo": "SlNo",
#         "TaskType": "Task Type",
#         "ProjectName": "Project",
#         "Title": "Task",
#         "TotalDuration": "Duration",
#         "StatusName": "Status"
#     }

#     exclude_fields = ["SortId", "ProjectTaskId", "ProjectId", "StartDate", "EndDate", "StaffName", "TaskAssignedTo", "CreatedDate", "Description", "CompletionPoint", "VerifiedBy"]
#     column_order = ["SlNo", "TaskType", "ProjectName", "Title", "TotalDuration", "StatusName"]

#     # Calculate maximum content widths for each column based on taskData
#     max_widths = {}
#     min_column_width = 100  # Minimum width for each column

#     for task in taskData:
#         for key in column_order:
#             if key not in exclude_fields:
#                 value = str(task.get(key, ""))
#                 max_widths[key] = max(max_widths.get(key, 0), len(value))

#     # Adjust column widths based on maximum content lengths
#     adjusted_widths = {}
#     for key in column_order:
#         if key not in exclude_fields:
#             adjusted_widths[key] = max(min_column_width, max_widths.get(key, 0) * 10)  # Adjust multiplier as needed

#     # Define the font and size for the text
#     font = ImageFont.load_default()
#     heading_font = ImageFont.load_default(28)

#     # Define the cell height
#     padding = 20
#     cell_height = 40

#     # Calculate image size
#     num_columns = len([key for key in column_order if key not in exclude_fields])
#     num_rows = len(taskData) + 1  # Including header row
#     content_width = sum(adjusted_widths.values())
#     content_height = num_rows * cell_height + 200  # +100 for logo and login/logout details

#     # Calculate total image dimensions including padding
#     image_width = content_width + 2 * padding
#     image_height = content_height + 2 * padding

#     # image_width = sum(adjusted_widths.values())
#     # image_height = num_rows * cell_height + 200  # +100 for logo and login/logout details

#     if image_width <= 0 or image_height <= 0:
#         raise ValueError("Calculated image dimensions are invalid. Ensure there is data to display.")

#     img = PILImage.new('RGB', (image_width, image_height), 'white')
#     draw = ImageDraw.Draw(img)

#     # Load and resize the left logo
#     logo_path_left = './static/images/logocubex.png'  
#     logo_left = PILImage.open(logo_path_left)
#     logo_left_width, logo_left_height = logo_left.size
#     max_logo_height = 25  

#     if logo_left_height > max_logo_height:
#         scaling_factor = max_logo_height / logo_left_height
#         new_logo_left_width = int(logo_left_width * scaling_factor)
#         new_logo_left_height = int(logo_left_height * scaling_factor)
#         logo_left = logo_left.resize((new_logo_left_width, new_logo_left_height), PILImage.LANCZOS)

#     # Load and resize the right logo
#     logo_path_right = './static/images/logo.png'  
#     logo_right = PILImage.open(logo_path_right)
#     logo_right_width, logo_right_height = logo_right.size

#     if logo_right_height > max_logo_height:
#         scaling_factor = max_logo_height / logo_right_height
#         new_logo_right_width = int(logo_right_width * scaling_factor)
#         new_logo_right_height = int(logo_right_height * scaling_factor)
#         logo_right = logo_right.resize((new_logo_right_width, new_logo_right_height), PILImage.LANCZOS)

#     # Calculate positions for logos at the center of the top line
#     total_logo_width = logo_left.width + logo_right.width
#     spacing = (image_width - total_logo_width-20) // 2  # Divide the remaining space into four parts for reduced spacing

#     logo_left_x = spacing
#     logo_left_y = (100 - logo_left.height) // 3
#     img.paste(logo_left, (logo_left_x, logo_left_y), logo_left)

#     logo_right_x = 1 * spacing + logo_left.width+20
#     logo_right_y = (100 - logo_right.height) // 3
#     img.paste(logo_right, (logo_right_x, logo_right_y), logo_right)

#     row_pos = max(logo_left_y + logo_left.height, logo_right_y + logo_right.height) + 20  

#     heading_text = f"{StaffName} - Daily Report"
#     bbox = heading_font.getbbox(heading_text)

#     heading_width = bbox[2] - bbox[0]
#     heading_height = bbox[3] - bbox[1]

#     heading_x = (image_width - heading_width) // 2
#     heading_y = row_pos  

#     # Draw the heading text on the image
#     draw.text((heading_x, heading_y), heading_text, fill='black', font=heading_font)
#     row_pos += 40



#     # col_pos = 30
#     # login_details_str = "\n".join(login_details)
#     # draw.text((col_pos, row_pos), login_details_str, fill='black', font=font)
#     # row_pos += 30 + len(login_details) * 20

#     # login_details = f"Logout Time: {logout_time}"
#     # draw.text((col_pos, row_pos), login_details, fill='black', font=font)
#     # row_pos += 30

#     # Draw headers
    
#     x0 = 20
#     for col_num, key in enumerate(column_order):
#         if key not in exclude_fields:
#             header = rename_mapping[key]
#             header_width = adjusted_widths[key]
#             x1 = x0 + header_width
#             y0 = row_pos
#             y1 = y0 + cell_height
#             draw.rectangle([x0, y0, x1, y1], outline='black')
#             draw.text((x0 + 10, y0 + 10), header, fill='black', font=font)
#             x0 = x1

#     row_pos += cell_height  # Move to the next row
#     y_bottom = row_pos + (num_rows * cell_height)
#     # draw.line([(0, y_bottom), (image_width, y_bottom)], fill='black')
    
#     for row_num, task in enumerate(taskData):
#         x0 =20
#         for col_num, key in enumerate(column_order):
#             if key not in exclude_fields:
#                 value = str(task.get(key, ""))
#                 column_width = adjusted_widths[key]
#                 x1 = x0 + column_width
#                 y0 = row_pos + (row_num * cell_height)
#                 y1 = y0 + cell_height
#                 draw.rectangle([x0, y0, x1, y1], outline='black')
#                 draw.text((x0 + 10, y0 + 10), value, fill='black', font=font)
#                 x0 = x1

#     # Draw bottom border for the table
    

#     img_stream = io.BytesIO()
#     img.save(img_stream, format='PNG')
#     img_stream.seek(0)

#     response = HttpResponse(img_stream, content_type='image/png')
#     response['Content-Disposition'] = f'attachment; filename={StaffName}DailyReport_{current_date}.png'

#     return response



from datetime import datetime
import io
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.decorators import api_view
from PIL import Image as PILImage, ImageDraw, ImageFont
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['GET'])
def StaffDailyReport(request, StaffId=""):
    current_date = timezone.now().date()
    staff = Staff.objects.get(StaffId=StaffId)
    StaffName = staff.StaffName

    projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    taskData = []
    serial_number = 1
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
        '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
        '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
        '%d/%m/%Y, %H:%M:%S'      # Example: 07/04/2024, 10:06:38
    ]

    for row in projectTaskSerializer.data:
        try:
            taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
            taskStatusSerializer = TaskStatusSerializer(taskStatus)
            row['StatusName'] = taskStatusSerializer.data['Status']
        except TaskStatus.DoesNotExist:
            row['StatusName'] = ""

        try:
            project = Project.objects.get(ProjectId=row['ProjectId'])
            projectSerializer = ProjectSerializer(project)
            row['ProjectName'] = projectSerializer.data['ProjectName']
        except Project.DoesNotExist:
            row['ProjectName'] = ""

        try:
            assigned_staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
            staffSerializer = StaffSerializer(assigned_staff)
            row['StaffName'] = staffSerializer.data['StaffName']
        except Staff.DoesNotExist:
            row['StaffName'] = ""

        taskData.append(row)  # Add task data to the list

    response_data = []

    try:
        login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('SortId')

        for login_history in login_histories:
            login_time = ""
            logout_time = ""

            for date_format in date_formats:
                try:
                    login_time_dt = datetime.strptime(login_history.LoginTime, date_format)
                    if login_time_dt and login_time_dt.date() == current_date:
                        login_time = login_history.LoginTime
                        logout_time = login_history.LogoutTime if login_history.LogoutTime else ""

                        if login_time:
                            login_details = {
                                "LoginTime": login_time,
                                "LogoutTime": logout_time,
                                "Tasks": []
                            }

                            for task in taskData:
                                task_timings = ProjectTaskTiming.objects.filter(
                                    ProjectTaskId=task['ProjectTaskId'],
                                    StartDate__range=(login_time, logout_time)
                                )
                                task_timing_serializer = ProjectTaskTimingSerializer(task_timings, many=True)

                                timing_data = []
                                for timing in task_timing_serializer.data:
                                    start_date = None
                                    for date_format in date_formats:
                                        try:
                                            start_date = datetime.strptime(timing['StartDate'], date_format)
                                            break
                                        except ValueError:
                                            continue

                                    if start_date and start_date.date() == current_date:
                                        timing_data.append(timing)

                                if timing_data:
                                    task['timing'] = timing_data
                                    task['SlNo'] = serial_number  # Add serial number to the task
                                    serial_number += 1
                                    login_details['Tasks'].append(task)

                            response_data.append(login_details)
                            break  # Stop checking other date formats once a match is found
                except ValueError:
                    continue

    except LoginHistory.DoesNotExist:
        pass

    rename_mapping = {
        "SlNo": "SlNo",
        "TaskType": "Task Type",
        "ProjectName": "Project",
        "Title": "Task",
        "TotalDuration": "Duration",
        "StatusName": "Status"
    }

    exclude_fields = ["SortId", "ProjectTaskId", "ProjectId", "StartDate", "EndDate", "StaffName", "TaskAssignedTo", "CreatedDate", "Description", "CompletionPoint", "VerifiedBy"]
    column_order = ["SlNo", "TaskType", "ProjectName", "Title", "TotalDuration", "StatusName"]

    # Calculate maximum content widths for each column based on taskData
    max_widths = {}
    min_column_width = 100  # Minimum width for each column

    for task in response_data:
        for key in column_order:
            if key not in exclude_fields:
                value = str(task.get(key, ""))
                max_widths[key] = max(max_widths.get(key, 0), len(value))

    # Adjust column widths based on maximum content lengths
    adjusted_widths = {}
    for key in column_order:
        if key not in exclude_fields:
            adjusted_widths[key] = max(min_column_width, max_widths.get(key, 0) * 10)  # Adjust multiplier as needed

    # Define the font and size for the text
    font = ImageFont.load_default()
    heading_font = ImageFont.load_default(28)

    # Define the cell height
    padding = 20
    cell_height = 40

    # Calculate image size
    num_columns = len([key for key in column_order if key not in exclude_fields])
    num_rows = len(response_data) + 1  # Including header row
    content_width = sum(adjusted_widths.values())
    content_height = num_rows * cell_height + 200  # +100 for logo and login/logout details

    # Calculate total image dimensions including padding
    image_width = content_width + 2 * padding
    image_height = content_height + 2 * padding

    # image_width = sum(adjusted_widths.values())
    # image_height = num_rows * cell_height + 200  # +100 for logo and login/logout details

    if image_width <= 0 or image_height <= 0:
        raise ValueError("Calculated image dimensions are invalid. Ensure there is data to display.")

    img = PILImage.new('RGB', (image_width, image_height), 'white')
    draw = ImageDraw.Draw(img)

    # Load and resize the left logo
    logo_path_left = './static/images/logocubex.png'  
    logo_left = PILImage.open(logo_path_left)
    logo_left_width, logo_left_height = logo_left.size
    max_logo_height = 25  

    if logo_left_height > max_logo_height:
        scaling_factor = max_logo_height / logo_left_height
        new_logo_left_width = int(logo_left_width * scaling_factor)
        new_logo_left_height = int(logo_left_height * scaling_factor)
        logo_left = logo_left.resize((new_logo_left_width, new_logo_left_height), PILImage.LANCZOS)

    # Load and resize the right logo
    logo_path_right = './static/images/logo.png'  
    logo_right = PILImage.open(logo_path_right)
    logo_right_width, logo_right_height = logo_right.size

    if logo_right_height > max_logo_height:
        scaling_factor = max_logo_height / logo_right_height
        new_logo_right_width = int(logo_right_width * scaling_factor)
        new_logo_right_height = int(logo_right_height * scaling_factor)
        logo_right = logo_right.resize((new_logo_right_width, new_logo_right_height), PILImage.LANCZOS)

    # Calculate positions for logos at the center of the top line
    total_logo_width = logo_left.width + logo_right.width
    spacing = (image_width - total_logo_width-20) // 2  # Divide the remaining space into four parts for reduced spacing

    logo_left_x = spacing
    logo_left_y = (100 - logo_left.height) // 3
    img.paste(logo_left, (logo_left_x, logo_left_y), logo_left)

    logo_right_x = 1 * spacing + logo_left.width+20
    logo_right_y = (100 - logo_right.height) // 3
    img.paste(logo_right, (logo_right_x, logo_right_y), logo_right)

    row_pos = max(logo_left_y + logo_left.height, logo_right_y + logo_right.height) + 20  

    heading_text = f"{StaffName} - Daily Report"
    bbox = heading_font.getbbox(heading_text)

    heading_width = bbox[2] - bbox[0]
    heading_height = bbox[3] - bbox[1]

    heading_x = (image_width - heading_width) // 2
    heading_y = row_pos  

    # Draw the heading text on the image
    draw.text((heading_x, heading_y), heading_text, fill='black', font=heading_font)
    row_pos += 40

    
      # Move to the next row

    
    for login_details in response_data:
        # Draw login details
        login_time = login_details["LoginTime"]
        logout_time = login_details["LogoutTime"]

        # Draw login details section
        login_details_str = f"Login Time: {login_time}     Logout Time: {logout_time}"
        draw.text((20, row_pos), login_details_str, fill='black', font=font)
        row_pos += 30
        if login_details["Tasks"]:
            x0 = 20  # Initial X position
            for col_num, key in enumerate(column_order):
                if key not in exclude_fields:
                    header = rename_mapping[key]
                    header_width = adjusted_widths[key]
                    x1 = x0 + header_width
                    y0 = row_pos
                    y1 = y0 + cell_height
                    draw.rectangle([x0, y0, x1, y1], outline='black')
                    draw.text((x0 + 10, y0 + 10), header, fill='black', font=font)
                    x0 = x1

            row_pos += cell_height

        # Draw tasks
        for task in login_details["Tasks"]:
            x0 = 20
            for col_num, key in enumerate(column_order):
                if key not in exclude_fields:
                    value = str(task.get(key, ""))
                    column_width = adjusted_widths[key]
                    x1 = x0 + column_width
                    y0 = row_pos
                    y1 = y0 + cell_height
                    draw.rectangle([x0, y0, x1, y1], outline='black')
                    draw.text((x0 + 10, y0 + 10), value, fill='black', font=font)
                    x0 = x1
            row_pos += cell_height  # Move to the next row within tasks

        row_pos += 10 
        # Draw bottom border for the table
        

    img_stream = io.BytesIO()
    img.save(img_stream, format='PNG')
    img_stream.seek(0)

    response = HttpResponse(img_stream, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename={StaffName}DailyReport_{current_date}.png'

    return response
