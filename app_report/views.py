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
from reportlab.lib.pagesizes import letter



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
        if TotalDuration_seconds == duration_seconds:
            point=point
        else:
            point = ((point) * value_percentage) / 100
    except:
        point = ((1) * value_percentage) / 100
    
    return point








@csrf_exempt
@api_view(['GET'])
def StaffDailyReportinPDFformat(request, StaffId=""):
    current_date = timezone.now().date()
    staff = Staff.objects.get(StaffId=StaffId)
    StaffName = staff.StaffName

    projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    taskData = []
    serial_number = 1
    date_formats = [
        '%m/%d/%Y, %I:%M:%S %p',
        '%m/%d/%Y, %H:%M:%S',
        '%d/%m/%Y, %I:%M:%S %p',
        '%d/%m/%Y, %H:%M:%S'
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
    totalPoint=0

    try:
        login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('SortId')

        for login_history in login_histories:
            login_time = ""
            logout_time = ""

            for date_format in date_formats:
                try:
                    if login_history.LoginTime and login_history.LogoutTime:
                        login_time_dt = datetime.strptime(login_history.LoginTime, date_format)
                        if login_time_dt and login_time_dt.date() == current_date:
                            login_time = login_history.LoginTime
                            logout_time = login_history.LogoutTime if login_history.LogoutTime else ""

                            if login_time:
                                login_details = {
                                    "LoginTime": login_time,
                                    "LogoutTime": logout_time,
                                    "Tasks": [],
                                    "TotalWorkTime": 0  # Initialize total work time for this login period
                                }

                                total_login_work_time = 0  # Initialize total work time for this login period
                                
                                for task in taskData:


                                    task_timings = ProjectTaskTiming.objects.filter(
                                        ProjectTaskId=task['ProjectTaskId'],
                                        StartDate__range=(login_time, logout_time),
                                        EndDate__range=(login_time, logout_time)
                                    ).order_by('SortId')

                                    

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
                                            hours, minutes = map(int, timing['Duration'].split(':'))
                                            total_duration_minutes = hours * 60 + minutes
                                            total_login_work_time += total_duration_minutes
                                           
                                            if task['TotalDuration']:
                                                Duration = task['Duration']
                                                duration_seconds=durationCalculation(Duration)
                                                TotalDuration = task['TotalDuration']
                                                TotalDuration_seconds=durationCalculation(TotalDuration)
                                                point = task['TaskPoint']
                                                point = task['TaskPoint']
                                                totalPoint += pointCalculation(duration_seconds, TotalDuration_seconds, point)
                                                
                                            timing_data.append(timing)

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

    PendingTask = ProjectTask.objects.filter(Q(Status='1') | Q(Status='2'), TaskAssignedTo=StaffId)
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
        "totalPoint":round(totalPoint,2)
    }

    pdf = generate_pdf_with_watermark('dailyreport.html', context)
    invoice_file_name = f'{StaffName}.pdf'
    return HttpResponse(pdf.content, content_type='application/pdf')



def create_watermark(text):
    # Create a PDF file with the watermark text
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
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

def generate_pdf_with_watermark(request, context):
   
    pdf = render_to_pdf('dailyreport.html', context)
    
    
    watermark_pdf = create_watermark("CRM")

    
    input_pdf = PdfReader(BytesIO(pdf.content))

    
    output_pdf_stream = add_watermark(input_pdf, watermark_pdf)

   
    response = HttpResponse(output_pdf_stream.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename={context["StaffName"]}.pdf'
    return response