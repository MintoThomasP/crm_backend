from itertools import count
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
from django.http import HttpResponse
from app_category.models import Category, Report
from app_category.serializers import CategorySerializer, ReportSerializer

from app_default.models import TaskStatus
from app_default.serializers import TaskStatusSerializer
from app_default.views import retry
from app_login.models import LoginHistory
from app_login.serializers import LoginHistorySerializer
from app_project.models import Project, ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectSerializer, ProjectTaskSerializer, ProjectTaskTimingSerializer
from app_sale.views import render_to_pdf
from app_staff.models import Staff
from app_staff.serializers import StaffSerializer
# Create your views here.
from django.utils import timezone
import openpyxl
from datetime import datetime, timedelta
from django.db.models import Q
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4



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
        if staffData.get('StartDate') and staffData.get('EndDate'):
            project_tasks = ProjectTask.objects.filter(ProjectId=Project_id, TaskAssignedTo=staff_name,ScheduledDeadline__range=(start_date, end_date))
        else:
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
                if task_data['TaskType']=='Task' and task_data['Status'] != '1':
                    if task_data['TotalDuration']:
                        Duration = task_data['Duration']
                        duration_seconds=durationCalculation(Duration)
                        
                        TotalDuration = task_data['TotalDuration']
                        TotalDuration_seconds=durationCalculation(TotalDuration)
                        point = task_data['TaskPoint']
                    
                        Staff_details['TotalCompletedPoints'] += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)

                        # Staff_details['TotalCompletedPoints'] += round((task_data['TaskPoint']) - point, 2)
                        if TotalDuration_seconds < duration_seconds:
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
                        Staff_details['CompletedPoint'] += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)
                        # Staff_details['CompletedPoint'] += round((task_data['TaskPoint']) - point, 2)
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
            project_tasks_filtered = project_tasks.filter(ProjectId=project.ProjectId,CreatedDate__range=(start_date, end_date),TaskType='Task')
        else:
            project_tasks_filtered = project_tasks.filter(ProjectId=project.ProjectId,TaskType='Task')
           
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
                project_details['TotalCompletedPoints'] += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)
                #  round((task.TaskPoint) - point, 2)
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
        if TotalDuration_seconds == duration_seconds:
            point=point
        else:
            pointPercent = ((point) * value_percentage) / 100
            point=point-pointPercent

    except:
        pointPercent = ((1) * value_percentage) / 100
        point=point-pointPercent
    
    return point








@csrf_exempt
@api_view(['GET'])
def StaffDailyReportinPDFformat(request, StaffId=""):
    current_date = timezone.now().date()
    staff = Staff.objects.get(StaffId=StaffId)
    StaffName = staff.StaffName
    totalPoint=0
    projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    taskData = []
    serial_number = 1
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',
        '%m/%d/%Y, %H:%M:%S',
        '%d/%m/%Y, %I:%M:%S %p',
        '%d/%m/%Y, %H:%M:%S',
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%dT%H:%M:%S%z"
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
        

        taskData.append(row)

    response_data = []
    total_work_time = 0
    

    try:
        login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('SortId')

        for login_history in login_histories:
            login_time = ""
            logout_time = ""
            for date_format in date_formats:
                try:
                    if login_history.LoginTime and login_history.LogoutTime:
                        login_time_dt = datetime.strptime(login_history.LoginTime, date_format)
                        logout_time_dt = datetime.strptime(login_history.LogoutTime, date_format)
                        if login_time_dt and login_time_dt.date() == current_date:
                            login_time = login_history.LoginTime
                            logout_time = login_history.LogoutTime if login_history.LogoutTime else ""
                            
                            if login_time:
                                login_details = {
                                    "LoginTime": login_time_dt.strftime('%B %d, %Y, %I:%M:%S %p'),
                                    "LogoutTime": logout_time_dt.strftime('%B %d, %Y, %I:%M:%S %p'),
                                    "Tasks": [],
                                    "TotalWorkTime": 0  
                                }

                                total_login_work_time = 0 
                               
                                for task in taskData:
                                    task_timings = ProjectTaskTiming.objects.filter(
                                        ProjectTaskId=task['ProjectTaskId'],
                                        StartDate__range=(login_time, logout_time),
                                        EndDate__range=(login_time, logout_time)
                                    ).order_by('-SortId')
                                 

                                    

                                    task_timing_serializer = ProjectTaskTimingSerializer(task_timings, many=True)

                                    timing_data = []
                                    for timing in task_timing_serializer.data:
                                        start_date = None
                                        for date_format in date_formats:
                                            try:
                                                start_date = datetime.strptime(timing['StartDate'], date_format)
                                                end_date = datetime.strptime(timing['EndDate'], date_format)
                                                break
                                            except ValueError:
                                                continue
                                       
                                            
                                        if start_date and start_date.date() == current_date:
                                           
                                            try:
                                                hours, minutes = map(int, timing['Duration'].split(':'))
                                                total_duration_minutes = hours * 60 + minutes
                                                total_login_work_time += total_duration_minutes
                                            except:
                                                p=""
                                        timing['StartDate'] = start_date.strftime('%B %d, %Y, %I:%M:%S %p')
                                        timing['EndDate'] = end_date.strftime('%B %d, %Y, %I:%M:%S %p')
                                        
                                        
                                        if task['TotalDuration'] and task['TaskType']!='Ticket':
                                            Duration = task['Duration']
                                        
                                            duration_seconds=durationCalculation(Duration)
                                            
                                            TotalDuration = task['TotalDuration']
                                            TotalDuration_seconds=durationCalculation(TotalDuration)
                                            
                                            point = task['TaskPoint']
                                            totalPoint += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)
                                        timing_data.append(timing)
                                                
                                        # except:
                                        #     totalPoint +=0
                                        
    
                                            
                                    if timing_data:
                                        task['timing'] = timing_data
                                        login_details['Tasks'].append(task)

                                login_details['TotalWorkTime'] = total_login_work_time
                                total_work_time += total_login_work_time
                                response_data.append(login_details)
                                break
                except ValueError:
                    continue

    except LoginHistory.DoesNotExist:
        pass

    PendingTask = ProjectTask.objects.filter(Q(Status='1') | Q(Status='2'),Q(TaskType='Task')|Q(TaskType='Ticket'), TaskAssignedTo=StaffId,)
    PendingTaskSerializer = ProjectTaskSerializer(PendingTask, many=True)
    pendingDetails = []
    for col in PendingTaskSerializer.data:
        try:
            taskStatus = TaskStatus.objects.get(StatusId=col['Status'])
            taskStatusSerializer = TaskStatusSerializer(taskStatus)
            col['StatusName'] = taskStatusSerializer.data['Status']
        except TaskStatus.DoesNotExist:
            col['StatusName'] = ""

        try:
            project = Project.objects.get(ProjectId=col['ProjectId'])
            projectSerializer = ProjectSerializer(project)
            col['ProjectName'] = projectSerializer.data['ProjectName']
        except Project.DoesNotExist:
            col['ProjectName'] = ""
        for date_format in date_formats:
            try:
               
                deadline = col['ScheduledDeadline']
                scheduled_deadline = datetime.strptime(deadline, date_format).date()
               
                break
            except ValueError:
                continue
        else:
           
            
            scheduled_deadline = None


        if scheduled_deadline:
            if current_date < scheduled_deadline:
                col['StatusName'] = "Incoming"
              
            elif current_date > scheduled_deadline:
                col['StatusName'] = "Due"
              
            


        pendingDetails.append(col)
    total_duration_hours = total_work_time // 60
    total_duration_remaining_minutes = total_work_time % 60
    total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"


    context = {
        "StaffName": StaffName,
        "response_data": response_data,
        "current_date": current_date,
        "pendingDetails": pendingDetails,
        "total_work_time": total_duration, 
        "totalPoint":round(totalPoint,2),
        'pagesize':'A4',
    }
    # return JsonResponse(context,safe=False)
    pdf = render_to_pdf('dailyreport.html', context)
    
    
    watermark_pdf = create_watermark("CRM")

    
    input_pdf = PdfReader(BytesIO(pdf.content))

    
    output_pdf_stream = add_watermark(input_pdf, watermark_pdf)

   
    response = HttpResponse(output_pdf_stream.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={context["StaffName"]}.pdf'
    return HttpResponse(pdf.content, content_type='application/pdf')



    # pdf = generate_pdf_with_watermark('dailyreport.html', context)
    # invoice_file_name = f'{StaffName}.pdf'
    # return HttpResponse(pdf.content, content_type='application/pdf')



def create_watermark(text):
    # Create a PDF file with the watermark text
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 50)
    can.setFillColorRGB(0, 0, 0, 0.1)
    can.saveState()
    can.translate(300, 500)
    can.rotate(45)
    can.drawCentredString(0, 0, text)
    can.restoreState()
    can.save()
    packet.seek(0)
    return PdfReader(packet)

def add_watermark(input_pdf, watermark_pdf):
    output_pdf = PdfWriter()
    watermark_page = watermark_pdf.pages[0]

    for page in input_pdf.pages:
        page.merge_page(watermark_page)
        output_pdf.add_page(page)

    output_stream = BytesIO()
    output_pdf.write(output_stream)
    output_stream.seek(0)
    return output_stream

# def generate_pdf_with_watermark(request, context):
   
#     pdf = render_to_pdf('dailyreport.html', context)
    
    
#     watermark_pdf = create_watermark("CRM")

    
#     input_pdf = PdfReader(BytesIO(pdf.content))

    
#     output_pdf_stream = add_watermark(input_pdf, watermark_pdf)

   
#     response = HttpResponse(output_pdf_stream.read(), content_type='application/pdf')
#     response['Content-Disposition'] = f'attachment; filename={context["StaffName"]}.pdf'
#     return response


def dateConversion(Date):
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',
        '%m/%d/%Y, %H:%M:%S',
        '%d/%m/%Y, %I:%M:%S %p',
        '%d/%m/%Y, %H:%M:%S',
        "%Y-%m-%dT%H:%M:%S%z"
    ]
    for date_format in date_formats:
        try:
            ConvertedDate = datetime.strptime(Date, date_format)
            break
        except:
            p=""
        return ConvertedDate



# @csrf_exempt
# @api_view(['GET'])
# def StaffDailyReportinPDFformat(request, StaffId=""):
#     current_date = timezone.now().date()
#     staff = Staff.objects.get(StaffId=StaffId)
#     StaffName = staff.StaffName
#     totalPoint=0
#     projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
#     projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
#     taskData = []
#     serial_number = 1
#     date_formats = [
#         '%m/%d/%Y, %I:%M:%S %p',
#         '%m/%d/%Y, %H:%M:%S',
#         '%d/%m/%Y, %I:%M:%S %p',
#         '%d/%m/%Y, %H:%M:%S',
#         "%Y-%m-%dT%H:%M",
#         "%Y-%m-%dT%H:%M:%S%z"
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
        

#         taskData.append(row)

#     response_data = []
#     total_work_time=0

#     try:
#         login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('SortId')

#         for login_history in login_histories:
#             login_time = login_history.LoginTime
#             logout_time = login_history.LogoutTime if login_history.LogoutTime else ""

           
#             login_details = {
#                 "LoginTime": login_time,
#                 "LogoutTime": logout_time,
#                 "Timing": [],
#                 "TotalWorkTime": 0
#             }

            
#             total_login_work_time = 0

            
#             for task in taskData:
#                 task_timings = ProjectTaskTiming.objects.filter(
#                     ProjectTaskId=task['ProjectTaskId'],
#                     StartDate__range=(login_time, logout_time),
#                     EndDate__range=(login_time, logout_time)
#                 ).order_by('-SortId')

#                 task_timing_serializer = ProjectTaskTimingSerializer(task_timings, many=True)

#                 timing_data = []
#                 for timing in task_timing_serializer.data:
#                     start_date = None
#                     for date_format in date_formats:
#                         try:
#                             start_date = datetime.strptime(timing['StartDate'], date_format)
#                             end_date = datetime.strptime(timing['EndDate'], date_format)
#                             break
#                         except ValueError:
#                             continue
    
        
#                     if start_date and start_date.date() == current_date:
        
#                         try:
#                             hours, minutes = map(int, timing['Duration'].split(':'))
#                             total_duration_minutes = hours * 60 + minutes
#                             total_login_work_time += total_duration_minutes
#                         except:
#                             p=""
#                         timing_data.append({
#                             "SortId": timing['SortId'],
#                             "ProjectTaskTimingId": timing['ProjectTaskTimingId'],
#                             "ProjectTaskId": timing['ProjectTaskId'],
#                             "StartDate": start_date.strftime('%B %d, %Y, %I:%M:%S %p'),
#                             "EndDate": end_date.strftime('%B %d, %Y, %I:%M:%S %p'),
#                             "Duration": timing['Duration'],
#                             "Note": timing['Note'],
#                             "TaskDetails": task  # Append task details here
#                         })
#                         if task['TotalDuration'] and task['TaskType']!='Ticket':
#                             Duration = task['Duration']
                        
#                             duration_seconds=durationCalculation(Duration)
                            
#                             TotalDuration = task['TotalDuration']
#                             TotalDuration_seconds=durationCalculation(TotalDuration)
                            
#                             point = task['TaskPoint']
#                             totalPoint += round(pointCalculation(duration_seconds, TotalDuration_seconds, point),2)
#                         timing_data.append(timing)
                                
                       

#                 if timing_data:
#                     login_details['Timing'].extend(timing_data) 
                   
#                     login_details['Timing'].append(timing)

          
#             login_details['TotalWorkTime'] = total_login_work_time

          
#             response_data.append(login_details)

#     except LoginHistory.DoesNotExist:
#         pass

#     PendingTask = ProjectTask.objects.filter(Q(Status='1') | Q(Status='2'), TaskAssignedTo=StaffId)
#     PendingTaskSerializer = ProjectTaskSerializer(PendingTask, many=True)
#     pendingDetails = []
#     for col in PendingTaskSerializer.data:
#         try:
#             taskStatus = TaskStatus.objects.get(StatusId=col['Status'])
#             taskStatusSerializer = TaskStatusSerializer(taskStatus)
#             col['StatusName'] = taskStatusSerializer.data['Status']
#         except TaskStatus.DoesNotExist:
#             col['StatusName'] = ""

#         try:
#             project = Project.objects.get(ProjectId=col['ProjectId'])
#             projectSerializer = ProjectSerializer(project)
#             col['ProjectName'] = projectSerializer.data['ProjectName']
#         except Project.DoesNotExist:
#             col['ProjectName'] = ""
#         for date_format in date_formats:
#             try:
            
#                 deadline = col['ScheduledDeadline']
#                 scheduled_deadline = datetime.strptime(deadline, date_format).date()
            
#                 break
#             except ValueError:
#                 continue
#         else:
        
            
#             scheduled_deadline = None


#         if scheduled_deadline:
#             if current_date < scheduled_deadline:
#                 col['StatusName'] = "Incoming"
            
#             elif current_date > scheduled_deadline:
#                 col['StatusName'] = "Due"
            
            


#         pendingDetails.append(col)
#     total_duration_hours = total_work_time // 60
#     total_duration_remaining_minutes = total_work_time % 60
#     total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"


#     context = {
#         "StaffName": StaffName,
#         "response_data": response_data,
#         "current_date": current_date,
#         "pendingDetails": pendingDetails,
#         "total_work_time": total_duration, 
#         "totalPoint":round(totalPoint,2),
#         'pagesize':'A4',
#     }
#     return JsonResponse(context,safe=False)
    # pdf = render_to_pdf('dailyreport.html', context)
    
    
    # watermark_pdf = create_watermark("CRM")

    
    # input_pdf = PdfReader(BytesIO(pdf.content))

    
    # output_pdf_stream = add_watermark(input_pdf, watermark_pdf)

   
    # response = HttpResponse(output_pdf_stream.read(), content_type='application/pdf')
    # response['Content-Disposition'] = f'attachment; filename={context["StaffName"]}.pdf'
    # return HttpResponse(pdf.content, content_type='application/pdf')


# # from collections import defaultdict
# def get_subcategories(category_id):
#     subcategories = Category.objects.filter(RefId=category_id, ActiveStatus=1)
#     subcategory_serializer = CategorySerializer(subcategories, many=True)
#     subcategory_data = []
#     for subcategory in subcategory_serializer.data:
#         children = get_subcategories(subcategory['CategoryId'])
#         if children:
#             subcategory['Subcategory'] = children
#         report_data = get_report_data(subcategory['CategoryId'])
#         if report_data:
#             subcategory['Report'] = report_data
#         subcategory_data.append(subcategory)
#     return subcategory_data

# def get_report_data(category_id):
#     reports = Report.objects.filter(CategoryId=category_id)
#     report_serializer = ReportSerializer(reports, many=True)
#     return report_serializer.data

# @csrf_exempt
# @api_view(['GET'])
# def PandLReport(request):
#     if request.method == 'GET':
#         categories = Category.objects.filter(
#             Q(RefId__isnull=True) | Q(RefId=""),
#             ActiveStatus=1,
#             SectionType='2'
#         ).order_by('-SortId')
#         category_serializer = CategorySerializer(categories, many=True)
#         category_data = []
#         for category in category_serializer.data:
#             subcategories = get_subcategories(category['CategoryId'])
#             if subcategories:
#                 category['Subcategory'] = subcategories
#             report_data = get_report_data(category['CategoryId'])
#             if report_data:
#                 category['Report'] = report_data
#             category_data.append(category)
#         # categorized_data = categorize_by_month_and_year(category_data)
#         context = {
#             "category_data": category_data,
#         }
#         # pdf = render_to_pdf('pandl_report.html', context)
#         # return HttpResponse(pdf.content, content_type='application/pdf')
#         return JsonResponse(category_data, safe=False)

# def categorize_by_month_and_year(data):
#     def process_reports(reports):
#         categorized_reports = defaultdict(lambda: defaultdict(list))
#         for report in reports:
#             year_month = f"{report['Month']}-{report['Year']}"
#             categorized_reports[year_month]['reports'].append(report)
#         return categorized_reports

#     def process_item(item, categorized_data):
#         if 'Report' in item:
#             categorized_reports = process_reports(item['Report'])
#             for year_month, reports in categorized_reports.items():
#                 if year_month not in categorized_data:
#                     categorized_data[year_month] = defaultdict(list)
#                 categorized_data[year_month]['categories'].append({
#                     'category': item,
#                     'reports': reports['reports']
#                 })
#             del item['Report']

#         if 'Subcategory' in item:
#             for subcategory in item['Subcategory']:
#                 process_item(subcategory, categorized_data)

#     categorized_data = defaultdict(lambda: defaultdict(list))
#     for item in data:
#         process_item(item, categorized_data)

#     return categorized_data


# from collections import OrderedDict
# from itertools import groupby
# from operator import itemgetter
# @api_view(['GET'])
# @csrf_exempt
# def PandLReport(request):
#     if request.method == 'GET':
#         reports = Report.objects.all()
#         reportSerializer = ReportSerializer(reports, many=True)
#         reportData = []

#         # Sort reports by year and month
#         sorted_reports = sorted(reportSerializer.data, key=itemgetter('Year', 'Month'))

#         # Group reports by year and month
#         for year_month, group in groupby(sorted_reports, key=itemgetter('Year', 'Month')):
#             year, month = year_month
#             grouped_data = {
#                 'Year': year,
#                 'Month': month,
#                 'Reports': []
#             }

#             for row in group:
#                 category_id = row['CategoryId']
                
#                 try:
#                     category = Category.objects.get(CategoryId=category_id)
#                     categorySerializer = CategorySerializer(category)
#                     row['categoryData'] = categorySerializer.data

#                     if category.RefId:
#                         row['subcategories'] = (get_subcategories(category.RefId))
#                     else:
#                         row['subcategories'] = []
                    
#                     grouped_data['Reports'].append(row)
#                 except Category.DoesNotExist:
#                     pass

#             reportData.append(grouped_data)
#         context = {
#             "reportData": reportData,
#         }
#         pdf = render_to_pdf('pandl_report.html', context)
#         return HttpResponse(pdf.content, content_type='application/pdf')

#         # return JsonResponse(reportData, safe=False)

# def get_subcategories(ref_id):
#     try:
#         category = Category.objects.get(CategoryId=ref_id)
#         categorySerializer = CategorySerializer(category)
#         subcategory_data = {
#             'categoryData': categorySerializer.data,
#             'subcategories': []
#         }
        
       
#         if category.RefId:
#             subcategory_data['subcategories'] = get_subcategories(category.RefId)
        
#         return subcategory_data
#     except Category.DoesNotExist:
#         return []



from collections import defaultdict
from django.db.models import Q


def get_subcategories(category_id, startDate, startYear, endDate, endYear):
    subcategories = Category.objects.filter(RefId=category_id, ActiveStatus=1)
    subcategory_serializer = CategorySerializer(subcategories, many=True)
    subcategory_data = []
    for subcategory in subcategory_serializer.data:
        if 'CategoryId' not in subcategory:
            continue  # Skip if CategoryId is not found
        subcategory_entry = {
            "categoryname": subcategory['Category'],
        }
        children = get_subcategories(subcategory['CategoryId'], startDate, startYear, endDate, endYear)
        if children:
            subcategory_entry["subcategory"] = children
        report_data = get_report_data(subcategory['CategoryId'], startDate, startYear, endDate, endYear)
        if report_data:
            subcategory_entry.update(report_data)
        subcategory_data.append(subcategory_entry)
    return subcategory_data

def get_report_data(category_id, startDate, startYear, endDate, endYear):
    start_date = datetime(year=int(startYear), month=int(startDate), day=1)
    end_date = datetime(year=int(endYear), month=int(endDate), day=1)
    reports = Report.objects.filter(
        Q(Year__gt=start_date.year) | (Q(Year=start_date.year) & Q(Month__gte=start_date.month)),
        Q(Year__lt=end_date.year) | (Q(Year=end_date.year) & Q(Month__lte=end_date.month)),
        CategoryId=category_id,
    ).order_by('Level')
    
    report_serializer = ReportSerializer(reports, many=True)
    report_data = defaultdict(float)
    
    for report in report_serializer.data:
        year_month = f"{report['Year']}{report['Month']}"
        report_data[year_month] = report['Amount']
    
    # Debugging: Print the report data for each category
    print(f"Report data for category_id {category_id}: {report_data}")
    
    return report_data

# @csrf_exempt
# @api_view(['GET'])
# def PandLReport(request, startdate="", enddate=""):
#     if request.method == 'GET':
#         start_date = startdate.split('-')
#         startDate = start_date[0]  # month
#         startYear = start_date[1]  # year
        
#         end_date = enddate.split('-')
#         endDate = end_date[0]  # month
#         endYear = end_date[1]  # year
#         current_year = int(startYear)
#         current_month = int(startDate)
#         end_year = int(endYear)
#         end_month = int(endDate)
#         header = ["Item"]
        
#         while current_year < end_year or (current_year == end_year and current_month <= end_month):
#             header.append(f"{current_year}-{current_month}")
#             if current_month == 12:
#                 current_month = 1
#                 current_year += 1
#             else:
#                 current_month += 1
        
#         formatted_data = [{i: header[i] for i in range(len(header))}]
#         responsedata = []  
#         category_data_dict = {}
#         for category in Category.objects.all():
#             category_data_dict[category.CategoryId] = {key: 0 for key in range(1, len(header))}

#         for col in formatted_data:
#             for key, value in col.items(): 
#                 if value == "Item":
#                     continue
                
#                 year, month = value.split('-') 
                
#                 reports = Report.objects.filter(Month=month, Year=year).order_by('SortId')
#                 reportSerializer = ReportSerializer(reports, many=True)
                
#                 for row in reportSerializer.data:
#                     category_id = row['CategoryId']
#                     amount = row['Amount']
#                     level = row['Level']  
                    
#                     if category_id not in category_data_dict:
#                         category_data_dict[category_id] = {key: 0 for key in range(1, len(header))}
                    
#                     if key in category_data_dict[category_id]:
#                         category_data_dict[category_id][key] = amount
#                     else:
#                         category_data_dict[category_id][key] = amount
                    
                  
#                     category_data_dict[category_id]['level'] = level

        
#         for category_id, data in category_data_dict.items():
#             category = Category.objects.get(CategoryId=category_id)
#             categorySerializer = CategorySerializer(category)
            
#             Categorydata = {
#                 'Level': data['level'], 
#                 '0': categorySerializer.data['Category'],
#                 **data  
#             }
#             responsedata.append(Categorydata)


@csrf_exempt
@api_view(['GET'])
def PandLReport(request, startdate="", enddate=""):
    if request.method == 'GET':
        start_date = startdate.split('-')
        startDate = start_date[0]  # month
        startYear = start_date[1]  # year
        
        end_date = enddate.split('-')
        endDate = end_date[0]  # month
        endYear = end_date[1]  # year
        current_year = int(startYear)
        current_month = int(startDate)
        end_year = int(endYear)
        end_month = int(endDate)
        header = ["Item"]
        
        while current_year < end_year or (current_year == end_year and current_month <= end_month):
            header.append(f"{current_year}-{current_month}")
            if current_month == 12:
                current_month = 1
                current_year += 1
            else:
                current_month += 1
        
        formatted_data = [{i: header[i] for i in range(len(header))}]
        responsedata = []  
        category_data_dict = {}
        
        for category in Category.objects.all():
            category_data_dict[category.CategoryId] = {key: "" for key in range(1, len(header))}
            category_data_dict[category.CategoryId]['OrderNo'] = None  # Initialize level as None

        for col in formatted_data:
            for key, value in col.items(): 
                if value == "Item":
                    continue
                
                year, month = value.split('-') 
                
                reports = Report.objects.filter(Month=month, Year=year).order_by('OrderNo')
                reportSerializer = ReportSerializer(reports, many=True)
                
                for row in reportSerializer.data:
                    category_id = row['CategoryId']
                    amount = row['Amount']
                    level = row['OrderNo']  
                    
                    if key in category_data_dict[category_id]:
                        category_data_dict[category_id][key] = amount
                    else:
                        category_data_dict[category_id][key] = amount
                    
                   
                    if category_data_dict[category_id]['OrderNo'] is None or level > category_data_dict[category_id]['OrderNo']:
                        category_data_dict[category_id]['OrderNo'] = level
                    


       
        for category_id, data in category_data_dict.items():
            if data['OrderNo'] is None:
                continue 
            category = Category.objects.get(CategoryId=category_id)
            categorySerializer = CategorySerializer(category)
            
            Categorydata = {
                'OrderNo': data['OrderNo'], 
                '0': categorySerializer.data['Category'],
                **{k: v for k, v in data.items() if k != 'OrderNo'}  
            }
            responsedata.append(Categorydata)
        responsedata = sorted(responsedata, key=lambda x: x['OrderNo'])      
        context = {
            "formatted_data": formatted_data[0],
            "responsedata": responsedata
        }
        pdf = render_to_pdf('pandl_report.html', context)
        return HttpResponse(pdf.content, content_type='application/pdf')
        # return JsonResponse(context, safe=False)