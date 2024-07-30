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

from app_default.models import CategoryType, TaskStatus
from app_default.serializers import CategoryTypeSerializer, TaskStatusSerializer
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
from django.db.models import Sum



@csrf_exempt
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectReportApiByProjectId(request):
    staffData = JSONParser().parse(request)
    project = Project.objects.get(ProjectId=staffData['ProjectId'])
    projectSerializer = ProjectSerializer(project)
    ProjectDetails = projectSerializer.data

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
            
            Staff_details['TotalCompletedPoints'] =float(Staff_details['TotalCompletedPoints'])+ float(task_data['CompletionPoint'])
            if task_data['Status'] == '1' or task_data['Status'] == '2' or task_data['Status'] == '4' or task_data['Status'] == '5' or task_data['Status'] == '6':
                Staff_details['DueTaskCount'] += 1
            elif task_data['Status'] == '7' or task_data['Status'] == '8' or task_data['Status'] == '9':
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

                Staff_details['TotalCompletedPoints'] =float(Staff_details['TotalCompletedPoints'])+ float(task_data['CompletionPoint'])
                if task_data['Status'] == '1' or task_data['Status'] == '2' or task_data['Status'] == '4' or task_data['Status'] == '5' or task_data['Status'] == '6':
                    Staff_details['DueTaskCount'] += 1
                elif task_data['Status'] == '7' or task_data['Status'] == '8' or task_data['Status'] == '9':
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
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id, CreatedDate__range=(start_date, end_date),TaskType='Task')
    else:
        project_tasks = ProjectTask.objects.filter(TaskAssignedTo=staff_id,TaskType='Task')
        
    project_ids = project_tasks.values_list('ProjectId', flat=True).distinct()
    projects = Project.objects.filter(ProjectId__in=project_ids)
    staff_projects = []
    for project in projects:
        project_details = {
            'ProjectId': project.ProjectId,
            'ProjectName': project.ProjectName,
            'TotalCompletedPoints': 0.00,
            'TotalNumberofTask': 0,
            'DueTaskCount': 0,
            'CompletedTaskCount': 0,
            'OnTimeCompletedTaskCount': 0
        }
        if start_date and end_date:
            project_tasks_filtered = project_tasks.filter(ProjectId=project.ProjectId,CreatedDate__range=(start_date, end_date),TaskType='Task')
        else:
            project_tasks_filtered = project_tasks.filter(ProjectId=project.ProjectId,TaskType='Task')
           
        project_task_serializer = ProjectTaskSerializer(project_tasks_filtered, many=True)
        for task_data in project_task_serializer.data:
            project_details['TotalNumberofTask'] += 1
            project_details['TotalCompletedPoints'] =float(project_details['TotalCompletedPoints'])+ float(task_data['CompletionPoint'])
            
            if task_data['Status'] == '1' or task_data['Status'] == '2' or task_data['Status'] == '4' or task_data['Status'] == '5' or task_data['Status'] == '6':
                project_details['DueTaskCount'] += 1
            elif task_data['Status'] == '7' or task_data['Status'] == '8' or task_data['Status'] == '9':
                project_details['CompletedTaskCount'] += 1
            if  task_data['Status'] == '9':
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


def pointCalculation(projectTask):
    # end_datetime=projectTask['EndDate']
    # start_datetime=projectTask['StartDate']
    # scheduled_datetime=projectTask['ScheduledDeadline']
    scheduled_duration=projectTask['Duration']
    allotted_points=projectTask['TaskPoint']
    time_taken=durationCalculation(projectTask['TotalDuration'])
    # time_taken = (end_datetime - start_datetime).total_seconds() / 60  # Time taken in minutes
    scheduled_duration = durationCalculation(scheduled_duration) 
    # total_working_minutes = 8 * 60  # Total working hours in minutes
    # delay_minutes = (datetime(end_datetime) - datetime(scheduled_datetime)).total_seconds() / 60

    def clamp_points(points):
        if float(points)<((float(allotted_points) * (-2))):
            return -(allotted_points * 2)
        elif float(points)>((float(allotted_points) * (2))):
            return (allotted_points * 2)
        else:
            return float(points)
        # return max(-(allotted_points * 2), min(points, allotted_points * 2))
    if projectTask['Status']== '7' or projectTask['Status']== '8' or projectTask['Status']== '9' :
        if projectTask['Status']== '7':
            if time_taken == scheduled_duration:
                projectTask['CompletionPoint']= allotted_points  # Scenario 1
            elif time_taken > scheduled_duration:
                over_time_percentage = (time_taken/scheduled_duration) 
                projectTask['CompletionPoint']=  clamp_points(allotted_points * (1 - over_time_percentage))  # Scenario 2
            elif time_taken < scheduled_duration:
                under_time_percentage = (time_taken/scheduled_duration) 
                projectTask['CompletionPoint']=  clamp_points(allotted_points * (1 + under_time_percentage))  # Scenario 3
        else:
            delay_percentage = .5
            if time_taken == scheduled_duration:
                base_points = allotted_points * (1)  # Based on Scenario 1
            elif time_taken > scheduled_duration:
                over_time_percentage = (time_taken/scheduled_duration)  
                base_points = allotted_points * (1 - (delay_percentage*2)-over_time_percentage)  # Based on Scenario 2
            else:
                under_time_percentage = (time_taken/scheduled_duration) 
                base_points = allotted_points * (1 - (delay_percentage*1.5)+under_time_percentage )  # Based on Scenario 3
            
            projectTask['CompletionPoint']=  clamp_points(base_points - (allotted_points * 2))  # Adjusted by subtracting twice the task points


        # try:
        #     value_percentage = ((time_taken / scheduled_duration) * 100) - 100
        #     try:
        #         if time_taken == scheduled_duration:
        #             point=allotted_points
        #         else:
        #             pointPercent = ((allotted_points) * value_percentage) / 100
        #             point=allotted_points-pointPercent

        #     except:
        #         pointPercent = ((1) * value_percentage) / 100
        #         point=point-pointPercent
        
        # except:
        #     point=0
    return projectTask['CompletionPoint']








@csrf_exempt
@api_view(['GET'])
def StaffDailyReportinPDFformat(request, StaffId=""):
    current_date = timezone.now().date()
    current_datetime = timezone.now()
    staff = Staff.objects.get(StaffId=StaffId)
    StaffName = staff.StaffName
    totalPoint=0.00
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
                                        __range=(login_time, logout_time),
                                        EndDate__range=(login_time, logout_time)
                                    ).order_by('-SortId')
                                 

                                    

                                    task_timing_serializer = ProjectTaskTimingSerializer(task_timings, many=True)

                                    timing_data = []
                                    isFirstData=True
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
                                        totalPoint=totalPoint+float(task['CompletionPoint'])
                                        if isFirstData:
                                            task['StartDate']=timing['StartDate']
                                            task['EndDate']=timing['EndDate']
                                            task['Duration']=timing['Duration']

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

    PendingTask = ProjectTask.objects.filter(Q(Status='1')| Q(Status='10') | Q(Status='2'),Q(TaskType='Task')|Q(TaskType='Ticket'), TaskAssignedTo=StaffId,)
    PendingTaskSerializer = ProjectTaskSerializer(PendingTask, many=True)
    pendingDetails = []
    for col in PendingTaskSerializer.data:
        try:
            taskStatus = TaskStatus.objects.get(StatusId=col['Status'])
            taskStatusSerializer = TaskStatusSerializer(taskStatus)
            col['StatusName'] = taskStatusSerializer.data['Status']
            if col['Status']== '3' or col['Status']== 3:
                col['StatusName'] = col['StatusName'] + " - Not Verified"
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
                scheduled_deadline = datetime.strptime(deadline, date_format)
               
                break
            except ValueError:
                continue
        else:
           
            
            scheduled_deadline = None


        if scheduled_deadline:
            print(current_date)
            print(scheduled_deadline)
            if col['Status'] == '10':
                col['StatusName'] = "Pause"

            elif current_datetime < scheduled_deadline:
                col['StatusName'] = "Incoming"
            
            elif current_datetime > scheduled_deadline:
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
    
    return report_data


@csrf_exempt
@api_view(['GET'])
def FinanceReportPDF(request, startdate="", enddate="",ClientId="",ReportType="",NoOfMonths=""):
    context = getFinanceReport(request, startdate, enddate,ClientId ,ReportType,NoOfMonths)
    if ReportType=='1':
        pdf = render_to_pdf('pandl_report.html', context)
        # return JsonResponse(context,safe=False)
        return HttpResponse(pdf.content, content_type='application/pdf')
    elif ReportType=='2':
        pdf = render_to_pdf('balance_report.html', context)
        # return JsonResponse(context,safe=False)
        return HttpResponse(pdf.content, content_type='application/pdf')
  
@csrf_exempt
@api_view(['GET'])
def FinanceReport(request, startdate="", enddate="",ClientId="",ReportType=""):
    context = getFinanceReport(request, startdate, enddate,ClientId ,ReportType)
    return JsonResponse(context,safe=False)
    
def getFinanceReport(request, startdate="", enddate="",ClientId="",ReportType="",NoOfMonths="0"):
    # try :
        if request.method == 'GET':
            expectField=['OrderNo', 'Level','RefId','CategoryId']
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
                if ReportType=='1':
                    header.append("%")
            if ReportType=='1':
                header.append("YTD-"+str(timezone.now().year))
            if ReportType=='1':
                header.append("%")
            formatted_data = [{i: header[i] for i in range(len(header))}]
            responsedata = []  
            category_data_dict = {}
            datcount=0

            for col in formatted_data:
                reportSerializerData=[]
                for key, value in col.items(): 
                    try:
                        if value in ['Item']:
                            continue
                        year, month = value.split('-') 
                        reportData=[]
                        if year=='YTD' and  ReportType=='1':
                            reportData=getYTD(ClientId,ReportType)
                        else:
                            reports = Report.objects.filter(Month=month, Year=year,ClientId=ClientId,ReportType=ReportType).order_by('OrderNo')
                            reportSerializer = ReportSerializer(reports, many=True)
                            reportData=reportSerializer.data
                        for row in reportData:
                            category_id = row['CategoryId']
                            amount = row['Amount']
                            OrderNo = row['OrderNo']  
                            Level = row['Level']  
                            
                            try:
                                if key in category_data_dict[category_id]:
                                    category_data_dict[category_id][key] = amount
                                
                            
                            except:
                                category_data_dict[category_id]=[]
                                category_data_dict[category_id] = {key: "" for key in range(1, len(header))}
                                category_data_dict[category_id]['OrderNo'] = None  # Initialize level as None
                            if key in category_data_dict[category_id]:
                                category_data_dict[category_id][key] = amount
                            if category_data_dict[category_id]['OrderNo'] is None or OrderNo > category_data_dict[category_id]['OrderNo']:
                                category_data_dict[category_id]['OrderNo'] = OrderNo
                                category_data_dict[category_id]['Level'] = Level
                            
                    except:

                        p=""
            cell_length=2
            
            LevelAmount={}
            BaseValue={}
            LevelIndex=""
            isFirst=True
            isBaseValue=False
            for category_id, data in category_data_dict.items():
                if data['OrderNo'] is None:
                    continue 
                try:
                    category = Category.objects.get(CategoryId=category_id)
                    categorySerializer = CategorySerializer(category)
                    cell_length=len(data.items())-1
                    RefId=""
                    if categorySerializer.data['RefId']:
                        RefId=categorySerializer.data['RefId']
                    else:
                        RefId=categorySerializer.data['CategoryType']
                    Categorydata = {
                        'OrderNo': data['OrderNo'], 
                        '0': categorySerializer.data['Category'],
                        'Level': data['Level'],
                        'RefId':  RefId,
                        'CategoryId':  categorySerializer.data['CategoryId'],
                        **{k: v for k, v in data.items() if k not in expectField and k!='0'}  
                    }
                except:
                    if isFirst ==False and isBaseValue==False:

                        Categorydata = {
                            'OrderNo': data['OrderNo'], 
                            '0': "Total",
                            'Level': 1,
                            'RefId': "",
                            'CategoryId':  "TOTALID",
                            **{k: v for k, v in LevelAmount[LevelIndex].items() if k not in expectField and k!='0'}  
                        }
                        responsedata.append(Categorydata)
                    LevelIndex="level-"+category_id
                    LevelAmount[LevelIndex]={}
                    category = CategoryType.objects.get(
                        CategoryTypeId=category_id)
                    categorySerializer = CategoryTypeSerializer(
                        category)
                    if categorySerializer.data['UsageType']=="Base Value":
                        isBaseValue=True
                    elif (isFirst and len(BaseValue.items()))or(isFirst and ReportType=='2'):
                        isBaseValue=False
                        isFirst=False
                        Categorydata = {
                            'OrderNo': data['OrderNo'], 
                            '0': "Total",
                            'Level': 1,
                            'RefId': "",
                            'CategoryId':  "TOTALID",
                            **{k: v for k, v in BaseValue.items() if k not in expectField and k!='0'}  
                        }
                        responsedata.append(Categorydata)
                    
                    cell_length=len(data.items())-1
                    datcount+=1
                    Categorydata = {
                        'OrderNo': data['OrderNo'], 
                        '0': categorySerializer.data['CategoryType'],
                        'Level': data['Level'],
                        'RefId': "",
                        'CategoryId':  str(categorySerializer.data['CategoryTypeId']),
                        **{k: v for k, v in data.items() if k not in expectField and k!='0'}  
                    }
                for k, v in data.items():
                    amount=0
                    if k not in expectField and k !='0' and k !=0 and v!='null' and v and v is not None:
                        amount=v
                    try:
                        if isBaseValue:
                            BaseValue[k]=int(BaseValue[k])+int(amount)
                        else:
                            LevelAmount[LevelIndex][k]=int(LevelAmount[LevelIndex][k])+int(amount)
                    except:
                        if isBaseValue:
                            BaseValue[k]=0
                            BaseValue[k]=int(BaseValue[k])+int(amount)
                        else:
                            LevelAmount[LevelIndex][k]=0
                            LevelAmount[LevelIndex][k]=int(LevelAmount[LevelIndex][k])+int(amount)
                        
                responsedata.append(Categorydata)
            # if len(responsedata):
            Categorydata = {
                'OrderNo': len(responsedata)+1, 
                '0': "Total",
                'Level': 1,
                'RefId': "",
                'CategoryId':  "TOTALID",
                **{k: v for k, v in LevelAmount[LevelIndex].items() if k not in expectField and k!='0'}  
            }
            responsedata.append(Categorydata)
            responsedata = sorted(responsedata, key=lambda x: x['OrderNo'])
            # data = []
            data = []

            for cat_data in responsedata:
                amount = 0.00
                key = ""
                item = {}
                
                for k, v in cat_data.items():
                    item[k] = ""

                    # Skip specific keys
                    if k in expectField:
                        item[k] = v
                        continue

                    # Identify amount and key
                    if v != 'null' and v and v is not None:
                        amount = v
                        key = k
                        item[k] = v

                    # Calculate percentage for even keys 2, 4, 6
                    elif int(k) % 2 == 0 and key and ReportType=='1':
                        base_value = BaseValue.get(key, None)
                        if base_value and base_value != 'null' and base_value is not None:
                            try:
                                base_value = float(base_value)
                                amount = float(amount)
                                v = round((amount / base_value) * 100,2)
                            except ValueError:
                                v = 0.00
                        else:
                            v = 0.00
                        if cat_data['Level']==1 :
                            if v!=0.0:
                                cat_data[k] = f"{v}%"
                                item[k] = cat_data[k]
                        else:
                            cat_data[k] = f"{v}%"
                            item[k] = cat_data[k]

                        amount = 0.00

                    # Default assignment for other keys
                    else:
                        item[k] = v
                
                data.append(item)


            context = {
                "formatted_data": formatted_data[0],
                "responsedata": responsedata,
                "cell_length":cell_length,
                "BaseValue":BaseValue,
                "expectField":expectField,
                "NoOfMonths":int(NoOfMonths)
,
            }
            return context
        
        # print(startdate, enddate,ClientId ,ReportType)
    # except:
    #     return "NODATA"

def getYTD(ClientId="",ReportType="",year="",month=""):
    if year=="":
        year = timezone.now().year
    if month=="":
        month = timezone.now().month
    queryset = Report.objects.filter(
            Month__gte=1, Month__lte=month,ClientId=ClientId,ReportType=ReportType,
            Year=year
        ).values(
            'CategoryId', 'OrderNo', 'Level',
            'ReportType',
            'ClientId',
            'CategoryId',
            'Comment',
            'OrderNo',
            'Level'
        ).annotate(
            Amount=Sum('Amount')
        ).order_by('OrderNo')
    queryset_list  = sorted(list(queryset), key=lambda x: x['OrderNo'])
    return queryset_list





@csrf_exempt
@api_view(['GET'])
def StaffTaskReportNasedOnDateinPDFformat(request, StaffId="", StartDate="", EndDate=""):
    current_datetime = timezone.now()
    staff = Staff.objects.get(StaffId=StaffId)
    StaffName = staff.StaffName
    totalPoint = 0.00
    projectTasks = ProjectTask.objects.filter(TaskAssignedTo=StaffId)
    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    taskData = []
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

    start_dt = timezone.datetime.strptime(StartDate, '%Y-%m-%d').date()
    end_dt = (timezone.datetime.strptime(EndDate, '%Y-%m-%d') + timezone.timedelta(days=1)).date()

    delta = timedelta(days=1)
    dates = []
    while start_dt <= end_dt:
        dates.append(start_dt.isoformat())
        start_dt += delta

    response_data = []
    total_work_time = 0
    for date in dates:
        try:
            login_histories = LoginHistory.objects.filter(UserId=StaffId).order_by('SortId')

            for login_history in login_histories:
                login_time = ""
                logout_time = ""
                try:
                    if login_history.LoginTime and login_history.LogoutTime:
                        login_time_dt = datetime.strptime(login_history.LoginTime, '%Y-%m-%dT%H:%M:%S%z')
                        logout_time_dt = datetime.strptime(login_history.LogoutTime, '%Y-%m-%dT%H:%M:%S%z')
                       
                        if login_time_dt and login_time_dt.date() == date:

                            print(login_time_dt.date())
                            print("date",date)
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
                                
                                task_timings_list = []
                                
                                for task in taskData:
                                    task_timings = ProjectTaskTiming.objects.filter(
                                        ProjectTaskId=task['ProjectTaskId'],
                                        StartDate__range=(login_time, logout_time),
                                        EndDate__range=(login_time, logout_time)
                                    ).order_by('-SortId')

                                    task_timing_serializer = ProjectTaskTimingSerializer(task_timings, many=True)

                                    timing_data = []
                                    isFirstData = True
                                    for timing in task_timing_serializer.data:
                                        start_date = None
                                        try:
                                            start_date = datetime.strptime(timing['StartDate'], '%Y-%m-%dT%H:%M:%S%z')
                                            end_date = datetime.strptime(timing['EndDate'], '%Y-%m-%dT%H:%M:%S%z')
                                            break
                                        except ValueError:
                                            continue
                                        
                                    if start_date and start_date.date() == date:
                                        try:
                                            hours, minutes = map(int, timing['Duration'].split(':'))
                                            total_duration_minutes = hours * 60 + minutes
                                            total_login_work_time += total_duration_minutes
                                        except:
                                            pass
                                        timing['StartDate'] = start_date.strftime('%B %d, %Y, %I:%M:%S %p')
                                        timing['EndDate'] = end_date.strftime('%B %d, %Y, %I:%M:%S %p')
                                        totalPoint += float(task['CompletionPoint'])
                                        if isFirstData:
                                            task['StartDate'] = timing['StartDate']
                                            task['EndDate'] = timing['EndDate']
                                            task['Duration'] = timing['Duration']

                                            timing_data.append(timing)
                                            
                                    if timing_data:
                                        task['timing'] = timing_data
                                        task_timings_list.append(task)

                                task_timings_list.sort(key=lambda x: datetime.strptime(x['StartDate'], '%B %d, %Y, %I:%M:%S %p'))
                                
                                for sorted_task in task_timings_list:
                                    login_details['Tasks'].append(sorted_task)

                                login_details['TotalWorkTime'] = total_login_work_time
                                total_work_time += total_login_work_time
                                response_data.append(login_details)
                                break
                except ValueError:
                    continue

        except LoginHistory.DoesNotExist:
            pass

    return JsonResponse(response_data,safe=False)