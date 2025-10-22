from datetime import datetime, date, timedelta
import calendar
from django.db import connection
from django.db.models import DateTimeField
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_company.models import Company
from app_company.serializers import CompanySerializer
from app_default.views import retry
from app_login.models import Login
from app_project.models import Project, ProjectTask, ProjectTaskTiming
from app_project.serializers import ProjectTaskSerializer
from rest_framework.parsers import JSONParser
from django.http.response import JsonResponse
import qrcode
from PIL import Image
from io import BytesIO
from app_default.models import LeaveStatus, LeaveType
from app_basic.models import Designation
from app_basic.serializers import DesignationSerializer
from app_default.serializers import LeaveStatusSerializer, LeaveTypeSerializer
from app_login.serializers import LoginSerializer
from app_project.views import CustomPageNumberPagination
from app_report.views import durationCalculation
from app_site.models import SiteSettings
from app_site.serializers import SiteSettingsSerializer
from app_staff.models import LeaveApplication, MoveOnRegister, SalarySlip, Staff, StaffBankDetails, StaffDocuments, StaffGuardian
import os
from app_staff.serializers import LeaveApplicationSerializer, MoveOnRegisterSerializer, SalarySlipSerializer, SaveStaffSerializer, StaffBankDetailsSerializer, StaffDocumentsSerializer, StaffGuardianSerializer, StaffPerformanceSerializer, StaffSerializer, UpdateStaffSerializer, UploadStaffDocumentsSerializer
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics
from django.db.models import Q
from django.db.models import Avg
from datetime import datetime
from django.utils import timezone
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.conf import settings
from datetime import datetime, timedelta
from dateutil.parser import isoparse


def parse_duration(duration_str):
    """Parses 'H:M' or 'H:M:S' string into timedelta."""
    try:
        parts = duration_str.strip().split(":")
        parts = list(map(int, parts))
        if len(parts) == 2:
            return timedelta(hours=parts[0], minutes=parts[1])
        elif len(parts) == 3:
            return timedelta(hours=parts[0], minutes=parts[1], seconds=parts[2])
    except Exception:
        pass
    return timedelta(0)


def get_total_task_duration_for_user(task_assigned_to, from_date_str, to_date_str):
    task_ids = ProjectTask.objects.filter(
        TaskAssignedTo=task_assigned_to
    ).values_list('ProjectTaskId', flat=True)

    # Step 2: Filter ProjectTaskTiming entries
    timings = ProjectTaskTiming.objects.filter(
        ProjectTaskId__in=task_ids
    ).exclude(Duration__isnull=True).exclude(Duration__exact="")

    if from_date_str and to_date_str:
        timings = timings.filter(
            StartDate__gte=from_date_str, EndDate__lte=to_date_str)
    elif from_date_str:
        timings = timings.filter(StartDate__gte=from_date_str)
    elif to_date_str:
        timings = timings.filter(EndDate__lte=to_date_str)
    total_duration = timedelta()

    for timing in timings:
        try:
            duration = parse_duration(timing.Duration)
            total_duration += duration
        except Exception:
            continue  # Skip malformed rows

    # Convert total_duration to H:M:S
    total_hours = total_duration.total_seconds() // 3600
    total_minutes = (total_duration.total_seconds() % 3600) // 60
    total_seconds = int(total_duration.total_seconds() % 60)

    return f"{int(total_hours):02}:{int(total_minutes):02}:{total_seconds:02}"


class getStaffReport(generics.ListAPIView):
    queryset = Staff.objects.filter(Status=1)
    serializer_class = StaffSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            company_id = filterData.get('CompanyId')

            # Apply CompanyId filter if provided
            if company_id:
                self.queryset = self.queryset.filter(CompanyId=company_id)

            if len(filterData['StaffId']):
                self.queryset = self.queryset.filter(
                    StaffId__in=filterData['StaffId'])

            # Parse FromDate and ToDate with appropriate format
            from_date_str = datetime.strptime(filterData.get(
                'FromDate', ''), '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M') if filterData.get('FromDate') else None
            to_date = datetime.strptime(filterData.get('ToDate', ''), '%Y-%m-%d') + timedelta(
                days=1) - timedelta(seconds=1) if filterData.get('ToDate') else None
            to_date_str = to_date.strftime(
                '%Y-%m-%dT%H:%M') if to_date else None

            serializer = self.get_serializer(self.queryset, many=True)
            data = []

            # Process each client row
            for row in serializer.data:
                designation = Designation.objects.get(
                    DesignationId=row['Designation'])
                designationSerializer = DesignationSerializer(designation)
                row['DesignationName'] = designationSerializer.data['Designation']
                project_tasks = ProjectTask.objects.filter(
                    TaskAssignedTo=row['StaffId'], TaskType="Task")

                # Filter by date range if provided
                if from_date_str and to_date_str:
                    project_tasks = project_tasks.filter(
                        CreatedDate__gte=from_date_str, CreatedDate__lte=to_date_str)
                elif from_date_str:
                    project_tasks = project_tasks.filter(
                        CreatedDate__gte=from_date_str)
                elif to_date_str:
                    project_tasks = project_tasks.filter(
                        CreatedDate__lte=to_date_str)

                project_task_serializer = ProjectTaskSerializer(
                    project_tasks, many=True)
                work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0,
                                     'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
                current_date = str(date.today())

                # Count task statuses
                for task in project_task_serializer.data:
                    if task['Status'] in ['1', '2']:
                        work_status_count['Pending'] += 1
                    if task['Status'] == '3':
                        work_status_count['Completed'] += 1
                    if task['CreatedDate'] < current_date and task['Status'] == '1':
                        work_status_count['Due'] += 1
                    if task['Status'] in ['8', '9']:
                        work_status_count['Delay Finished'] += 1
                    if task['Status'] in ['4', '5', '6']:
                        work_status_count['Not Completed'] += 1
                    if task['Status'] == '7':
                        work_status_count['Finished'] += 1
                row['WorkDuration'] = get_total_task_duration_for_user(
                    row['StaffId'], from_date_str, to_date_str)
                row['WorkStatusCount'] = work_status_count
                data.append(row)

            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({'error': str(e)}, safe=False, status=500)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=SaveStaffSerializer, operation_description="NOTE: API for save staff")
@swagger_auto_schema(method='PUT', request_body=SaveStaffSerializer, operation_description="NOTE: API for edit staff")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all Staff by company id",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def staffApi(request, CompanyId=""):
    try:
        if request.method == 'GET':

            staff = Staff.objects.filter(
                CompanyId=CompanyId, Status=1).order_by('-SortId')
            staffSerializer = StaffSerializer(
                staff, many=True)
            staffData = []
            for row in staffSerializer.data:
                designation = Designation.objects.get(
                    DesignationId=row['Designation'])
                designationSerializer = DesignationSerializer(designation)
                row['DesignationName'] = designationSerializer.data['Designation']

                projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=row['StaffId'], TaskType="Task")
                projectTaskSerializer = ProjectTaskSerializer(
                    projectTask, many=True)
                work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0,
                                     'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
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
                staffData.append(row)

            return JsonResponse(staffData, safe=False)
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
                loginData = {
                    "UserId": staffSerializer.data['StaffId'],
                    "EmailId": staffSerializer.data['EmailId'],
                    "UserType": staffSerializer.data['UserType'],
                    "Password": staffSerializer.data['StaffCode']


                }
                loginSerializer = LoginSerializer(data=loginData)
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
                loginData = {
                    "UserId": staffData['StaffId'],
                    "EmailId": staffSerializer.data['EmailId'],
                    "UserType": staffSerializer.data['UserType'],
                    "Password": staffSerializer.data['StaffCode']

                }
                try:
                    login = Login.objects.get(UserId=staffData['StaffId'])
                    loginSerializer = LoginSerializer(login, data=loginData)
                    if loginSerializer.is_valid():
                        loginSerializer.save()
                except:
                    loginSerializer = LoginSerializer(data=loginData)
                    if loginSerializer.is_valid():
                        loginSerializer.save()

                return JsonResponse(staffSerializer.data['StaffId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Staff by StaffId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete Staff by StaffId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def StaffApiById(request, StaffId=""):
    try:
        if request.method == 'GET':
            staff = Staff.objects.get(
                StaffId=StaffId)
            staffSerializer = StaffSerializer(
                staff)
            staffData = staffSerializer.data
            try:
                designation = Designation.objects.get(
                    DesignationId=staffSerializer.data['Designation'])
                designationSerializer = DesignationSerializer(designation)
                staffData['DesignationName'] = designationSerializer.data['Designation']
            except:
                staffData['DesignationName'] = ""

            projectTask = ProjectTask.objects.filter(
                TaskAssignedTo=staffSerializer.data['StaffId'], TaskType='Task')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0,
                                 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
            current_date = datetime.today()

            date_formats = [
                '%m/%d/%Y, %I:%M:%S %p',
                '%m/%d/%Y, %H:%M:%S',
                '%d/%m/%Y, %I:%M:%S %p',
                '%d/%m/%Y, %H:%M:%S',
                "%Y-%m-%dT%H:%M",
                "%Y-%m-%dT%H:%M:%S%z"
            ]
            total_point = 0
            total_points_gain = 0
            count = 0
            for task in projectTaskSerializer.data:
                scheduled_deadline = 0
                if task['Status'] == '7' or task['Status'] == '8' or task['Status'] == '9':
                    total_point = +float(task['TaskPoint'])
                    total_points_gain = total_points_gain + \
                        float(task['CompletionPoint'])
                    count = count+1
                for date_format in date_formats:
                    try:
                        deadline = task['ScheduledDeadline']
                        if deadline:
                            scheduled_deadline = datetime.strptime(
                                deadline, date_format)
                        break
                    except ValueError:
                        continue

                if task['Status'] == '1' or task['Status'] == '2':
                    work_status_count['Pending'] += 1

                if task['Status'] == '3':
                    work_status_count['Completed'] += 1

                if scheduled_deadline and scheduled_deadline < current_date and task['Status'] == '1' or task['Status'] == '2' or task['Status'] == '10':
                    work_status_count['Due'] += 1

                if task['Status'] == '8' or task['Status'] == '9':
                    work_status_count['Delay Finished'] += 1

                if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                    work_status_count['Not Completed'] += 1

                if task['Status'] == '7':
                    work_status_count['Finished'] += 1
            work_status_count['Performance'] = 0
            if count:
                work_status_count['Performance'] = total_points_gain/count
            staffData['WorkStatusCount'] = work_status_count
            return JsonResponse(staffData, safe=False)
        elif request.method == 'DELETE':
            staff = Staff.objects.get(StaffId=StaffId)
            staff.Status = 0
            staff.save()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Staff by StaffId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete Staff by StaffId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def DashboardData(request, StaffId=""):
    # try:
    if request.method == 'GET':
        try:
            staff = Staff.objects.get(
                StaffId=StaffId)
            staffSerializer = StaffSerializer(
                staff)
            staffData = staffSerializer.data
        except:
            staffData = []
        try:
            designation = Designation.objects.get(
                DesignationId=staffSerializer.data['Designation'])
            designationSerializer = DesignationSerializer(designation)
            staffData['DesignationName'] = designationSerializer.data['Designation']
        except:
            staffData['DesignationName'] = ""

        projectTask = ProjectTask.objects.filter(
            TaskAssignedTo=staffSerializer.data['StaffId'], TaskType='Task')
        projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
        work_status_count = {'Pending': 0, 'Paused': 0, 'Verfication pending': 0,
                             'On time': 0, 'Re-assigned': 0, 'Delay Finished': 0}

        current_date = datetime.today()

        date_formats = [
            '%m/%d/%Y, %I:%M:%S %p',
            '%m/%d/%Y, %H:%M:%S',
            '%d/%m/%Y, %I:%M:%S %p',
            '%d/%m/%Y, %H:%M:%S',
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%dT%H:%M:%S%z"
        ]
        total_point = 0
        total_points_gain = 0
        count = 0
        for task in projectTaskSerializer.data:
            scheduled_deadline = 0
            if task['Status'] == '7' or task['Status'] == '8' or task['Status'] == '9':
                total_point = +float(task['TaskPoint'])
                total_points_gain = total_points_gain + \
                    float(task['CompletionPoint'])
                count = count+1
            for date_format in date_formats:
                try:
                    deadline = task['ScheduledDeadline']
                    if deadline:
                        scheduled_deadline = datetime.strptime(
                            deadline, date_format)
                    break
                except ValueError:
                    continue

            if task['Status'] == '1' or task['Status'] == '2':
                work_status_count['Pending'] += 1

            if task['Status'] == '10':
                work_status_count['Paused'] += 1

            if task['Status'] == '3':
                work_status_count['Verfication pending'] += 1

            if task['Status'] == '7':
                work_status_count['On time'] += 1

            if task['Status'] == '8' or task['Status'] == '9':
                work_status_count['Delay Finished'] += 1

            if task['Status'] == '4' or task['Status'] == '5' or task['Status'] == '6':
                work_status_count['Re-assigned'] += 1

        work_status_count['Performance'] = 0
        if count:
            work_status_count['Performance'] = total_points_gain/count
        staffData['WorkStatusCount'] = work_status_count

# Define the date range: from 7 months ago to the start of next month
        sql = "WITH month_series AS ( SELECT DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL n MONTH), '%b') AS Month, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL n MONTH), '%Y') AS Year, DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL n MONTH), '%Y-%m-01') AS EndDate FROM (SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7) AS numbers ) SELECT ms.Month, COALESCE(SUM(t.TaskPoint), 0) AS TotalPoints FROM month_series ms LEFT JOIN app_project_projecttask t ON DATE_FORMAT(t.EndDate, '%Y-%m-01') = ms.EndDate AND TaskAssignedTo='" + \
            StaffId + \
            "' GROUP BY ms.Month, ms.Year ORDER BY ms.Year DESC, FIELD(ms.Month, 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec');"
        task_performance = connection.cursor()
        task_performance.execute(sql)
        field_names = [i[0] for i in task_performance.description]
        task_performance_data = []
        for task in task_performance.fetchall():
            j = 0
            task_data = {}
            for col in task:
                if j < len(field_names):
                    task_data[str(field_names[j])] = col
                    j = j + 1
            task_performance_data.append(task_data)
        staffData['7MonthPerformance'] = task_performance_data

        sql = "WITH RECURSIVE date_series AS ( SELECT CURDATE() - INTERVAL 6 DAY AS DateValue UNION ALL SELECT DateValue + INTERVAL 1 DAY FROM date_series WHERE DateValue + INTERVAL 1 DAY <= CURDATE() ) SELECT DATE_FORMAT(ds.DateValue, '%a') AS DayOfWeek, COALESCE(SUM(TIMESTAMPDIFF(HOUR, t.MoveOutDateTime, t.MoveInDateTime)), 0) AS TotalWorkingHours FROM date_series ds LEFT JOIN app_staff_moveonregister t ON DATE(t.MoveInDateTime) = ds.DateValue AND t.StaffId = '"+StaffId+"' GROUP BY ds.DateValue ORDER BY ds.DateValue;"
        task_performance = connection.cursor()
        task_performance.execute(sql)
        field_names = [i[0] for i in task_performance.description]
        task_performance_data = []
        for task in task_performance.fetchall():
            j = 0
            task_data = {}
            for col in task:
                if j < len(field_names):
                    task_data[str(field_names[j])] = col
                    j = j + 1
            task_performance_data.append(task_data)
        staffData['7DayWorkingHours'] = task_performance_data

        sql = "SELECT DATE(d.days) AS `Date`, DATE_FORMAT(d.days, '%a') AS `DayName`, COALESCE(COUNT(t.ProjectTaskId), 0) AS `TotalCompletedTasks` FROM ( SELECT CURDATE() - INTERVAL n DAY AS days FROM ( SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 ) AS numbers ) AS d LEFT JOIN app_project_projecttask t ON DATE(t.CreatedDate) = DATE(d.days) AND t.Status IN (7, 8, 9) AND TaskAssignedTo='"+StaffId+"' GROUP BY d.days ORDER BY d.days DESC;"
        task_performance = connection.cursor()
        task_performance.execute(sql)
        field_names = [i[0] for i in task_performance.description]
        task_performance_data = []
        for task in task_performance.fetchall():
            j = 0
            task_data = {}
            for col in task:
                if j < len(field_names):
                    task_data[str(field_names[j])] = col
                    j = j + 1
            task_performance_data.append(task_data)
        staffData['7DayTaskCount'] = task_performance_data

        return JsonResponse(staffData, safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StaffGuardianSerializer, operation_description="NOTE: API for save Staff Guardian")
@swagger_auto_schema(method='PUT', request_body=StaffGuardianSerializer, operation_description="NOTE: API for edit Staff Guardian")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all Staff's guardian details",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def staffGuardianApi(request):
    try:
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
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get StaffGuardian by staffGuardianId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete StaffGuardian by staffGuardianId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def staffGuardianApiById(request, StaffGuardianId=""):
    try:
        if request.method == 'GET':
            staffGuardian = StaffGuardian.objects.get(
                StaffGuardianId=StaffGuardianId)
            staffGuardianSerializer = StaffGuardianSerializer(
                staffGuardian)
            return JsonResponse(staffGuardianSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staffGuardian = StaffGuardian.objects.get(
                StaffGuardianId=StaffGuardianId)
            staffGuardian.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get StaffGuardian by StaffId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def staffGuardianApiByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET':
            staffGuardian = StaffGuardian.objects.filter(
                StaffId=StaffId)
            staffGuardianSerializer = StaffGuardianSerializer(
                staffGuardian, many=True)
            return JsonResponse(staffGuardianSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class uploadStaffProfileImage(APIView):
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
                    p = ""

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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Staff by StaffCode",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def staffApiByStaffCode(request, StaffCode=""):
    try:
        if request.method == 'GET':
            staff = Staff.objects.get(
                StaffCode=StaffCode)
            staffSerializer = StaffSerializer(
                staff)
            StaffData = staffSerializer.data
            try:
                designation = Designation.objects.get(
                    DesignationId=StaffData['Designation'])
                designationSerializer = DesignationSerializer(designation)
                StaffData['DesignationName'] = designationSerializer.data['Designation']
            except:
                StaffData['DesignationName'] = ""

            projectTask = ProjectTask.objects.filter(
                TaskAssignedTo=staffSerializer.data['StaffId'])
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0,
                                 'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
            current_date = datetime.today()

            date_formats = [
                '%m/%d/%Y, %I:%M:%S %p',
                '%m/%d/%Y, %H:%M:%S',
                '%d/%m/%Y, %I:%M:%S %p',
                '%d/%m/%Y, %H:%M:%S',
                "%Y-%m-%dT%H:%M",
                "%Y-%m-%dT%H:%M:%S%z"
            ]

            for task in projectTaskSerializer.data:
                for date_format in date_formats:
                    try:
                        deadline = task['ScheduledDeadline']
                        scheduled_deadline = datetime.strptime(
                            deadline, date_format)
                        break
                    except ValueError:
                        continue
                if task['Status'] == '1' or task['Status'] == '2':
                    work_status_count['Pending'] += 1

                if task['Status'] == '3':
                    work_status_count['Completed'] += 1

                if scheduled_deadline < current_date and task['Status'] == '1' or task['Status'] == '2' or task['Status'] == '10':
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
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StaffDocumentsSerializer, operation_description="NOTE: API for save StaffDocument")
@swagger_auto_schema(method='PUT', request_body=StaffDocumentsSerializer, operation_description="NOTE: API for edit StaffDocument")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all Staff's Documents details",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def staffDocumentsApi(request):
    try:
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
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get StaffDocument by StaffDocumentId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete StaffDocument by StaffDocumentId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def staffDocumentsApiById(request, StaffDocumentId=""):
    try:
        if request.method == 'GET':
            staffDocuments = StaffDocuments.objects.get(
                StaffDocumentId=StaffDocumentId)
            staffDocumentsSerializer = StaffDocumentsSerializer(
                staffDocuments)
            return JsonResponse(staffDocumentsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staffDocuments = StaffDocuments.objects.get(
                StaffDocumentId=StaffDocumentId)
            staffDocuments.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class uploadStaffDocuments(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, StaffDocumentId="", *args, **kwargs):
        try:

            staff = StaffDocuments.objects.get(
                StaffDocumentId=StaffDocumentId)
            try:
                StaffDocuments.objects.get(
                    StaffDocumentId=StaffDocumentId).Document.delete(save=True)
            except:
                p = ""

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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get StaffDocuments by StaffId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def staffDocumentsApiByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET':
            staffDocuments = StaffDocuments.objects.filter(
                StaffId=StaffId)
            staffDocumentsSerializer = StaffDocumentsSerializer(
                staffDocuments, many=True)
            return JsonResponse(staffDocumentsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all active Staff based on CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def GetAllActiveStaffListApi(request, CompanyId=""):
    try:
        if request.method == 'GET':

            staff = Staff.objects.filter(Status=1, CompanyId=CompanyId)
            staffSerializer = StaffSerializer(
                staff, many=True)
            staffData = []
            for row in staffSerializer.data:
                try:
                    designation = Designation.objects.get(
                        DesignationId=row['Designation'])
                    designationSerializer = DesignationSerializer(designation)
                    row['DesignationName'] = designationSerializer.data['Designation']
                except:
                    row['DesignationName'] = ""
                staffData.append(row)
            return JsonResponse(staffData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for Staff salary by performance",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def staffSalaryByPerformanceApi(request):
    if request.method == 'POST':
        requestData = JSONParser().parse(request)
        month = requestData['Month']
        year = requestData['Year']

        start_date = datetime(year, month, 1)

        end_date = start_date.replace(
            day=1, month=start_date.month % 12 + 1) - timedelta(days=1)

        projectTask = ProjectTask.objects.filter((Q(Status='7') | Q(Status='8') | Q(
            Status='9')), TaskAssignedTo=requestData['StaffId'], TaskType='Task', ScheduledDeadline__range=(start_date, end_date))
        projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)

        CompletedPoint = 0
        TaskPoint = 0

        for row in projectTaskSerializer.data:

            TaskPoint += int(row['TaskPoint'])
            CompletedPoint += float(row['CompletionPoint'])

        staff = Staff.objects.get(StaffId=requestData['StaffId'])
        staffSerializer = StaffSerializer(staff)

        try:
            Salary = float(staffSerializer.data['Salary'])
        except:
            Salary = 0
        if CompletedPoint < 0:
            Payment = Salary + ((Salary * 0.1) *
                                ((CompletedPoint / TaskPoint) * 100) / 100)
        elif CompletedPoint > TaskPoint:
            Payment = Salary + \
                ((Salary * 0.1) * (((CompletedPoint / TaskPoint) * 100) - 100) / 100)
        else:
            Payment = Salary

        return JsonResponse(Payment, safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=LeaveApplicationSerializer, operation_description="NOTE: API for save LeaveApplication")
@swagger_auto_schema(method='PUT', request_body=LeaveApplicationSerializer, operation_description="NOTE: API for edit LeaveApplication")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all LeaveApplication",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def leaveApplicationApi(request):
    try:
        if request.method == 'GET':

            leaveApplication = LeaveApplication.objects.all().order_by('-SortId')
            leaveApplicationSerializer = LeaveApplicationSerializer(
                leaveApplication, many=True)
            leaveData = []
            for row in leaveApplicationSerializer.data:
                try:
                    leaveStatus = LeaveStatus.objects.get(
                        StatusId=row['Status'])
                    leaveStatus_serializer = LeaveStatusSerializer(leaveStatus)
                    row['StatusName'] = leaveStatus_serializer.data['Status']
                except:
                    row['StatusName'] = ""
                try:
                    leaveType = LeaveType.objects.get(
                        LeaveTypeId=row['LeaveType'])
                    leaveType_serializer = LeaveTypeSerializer(leaveType)
                    row['LeaveTypeName'] = leaveType_serializer.data['LeaveType']
                except:
                    row['LeaveTypeName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['StaffId'])
                    staff_serializer = StaffSerializer(staff)
                    row['StaffName'] = staff_serializer.data['StaffName']
                except:
                    row['StaffName'] = ""
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
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get LeaveApplication by LeaveApplicationId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete LeaveApplication by LeaveApplicationId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def leaveApplicationApiById(request, LeaveApplicationId=""):
    try:
        if request.method == 'GET':
            leaveApplication = LeaveApplication.objects.get(
                LeaveApplicationId=LeaveApplicationId)
            leaveApplicationSerializer = LeaveApplicationSerializer(
                leaveApplication)
            return JsonResponse(leaveApplicationSerializer.data, safe=False)
        elif request.method == 'DELETE':
            leaveApplication = LeaveApplication.objects.get(
                LeaveApplicationId=LeaveApplicationId)
            leaveApplication.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class GetAllLeaveApplicationByCompanyId(generics.ListAPIView):
    queryset = LeaveApplication.objects.all().order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = LeaveApplicationSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(
                    CompanyId=filterData['CompanyId'])

            if Keyword:
                self.queryset = self.queryset.filter(
                    Q(Subject__icontains=Keyword) | Q(Description__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        leaveStatus = LeaveStatus.objects.get(
                            StatusId=row['Status'])
                        leaveStatus_serializer = LeaveStatusSerializer(
                            leaveStatus)
                        row['StatusName'] = leaveStatus_serializer.data['Status']
                    except:
                        row['StatusName'] = ""
                    try:
                        leaveType = LeaveType.objects.get(
                            LeaveTypeId=row['LeaveType'])
                        leaveType_serializer = LeaveTypeSerializer(leaveType)
                        row['LeaveTypeName'] = leaveType_serializer.data['LeaveType']
                    except:
                        row['LeaveTypeName'] = ""
                    try:
                        staff = Staff.objects.get(StaffId=row['StaffId'])
                        staff_serializer = StaffSerializer(staff)
                        row['StaffName'] = staff_serializer.data['StaffName']
                    except:
                        row['StaffName'] = ""
                    try:

                        staff = Staff.objects.get(StaffId=row['StaffId'])
                        staff_serializer = StaffSerializer(staff)
                        row['StaffName'] = staff_serializer.data['StaffName']
                    except:
                        row['StaffName'] = ""
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


class leaveApplicationApiByStaffId(generics.ListAPIView):
    queryset = LeaveApplication.objects.all().order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = LeaveApplicationSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['StaffId']:
                self.queryset = self.queryset.filter(
                    StaffId=filterData['StaffId'])

            if Keyword:
                self.queryset = self.queryset.filter(
                    Q(Subject__icontains=Keyword) | Q(Description__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        leaveStatus = LeaveStatus.objects.get(
                            StatusId=row['Status'])
                        leaveStatus_serializer = LeaveStatusSerializer(
                            leaveStatus)
                        row['StatusName'] = leaveStatus_serializer.data['Status']
                    except:
                        row['StatusName'] = ""
                    try:

                        leaveType = LeaveType.objects.get(
                            LeaveTypeId=row['LeaveType'])
                        leaveType_serializer = LeaveTypeSerializer(leaveType)
                        row['LeaveTypeName'] = leaveType_serializer.data['LeaveType']
                    except:
                        row['LeaveTypeName'] = ""
                    try:

                        staff = Staff.objects.get(StaffId=row['StaffId'])
                        staff_serializer = StaffSerializer(staff)
                        row['StaffName'] = staff_serializer.data['StaffName']
                    except:
                        row['StaffName'] = ""

                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


class StaffApiByCompanyIdPagination(generics.ListAPIView):
    queryset = Staff.objects.all().order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = StaffSerializer

    def post(self, request, *args, **kwargs):
        # try:
        filterData = JSONParser().parse(request)
        Keyword = filterData.get('SearchKeyword', '')
        if filterData['CompanyId']:
            self.queryset = self.queryset.filter(
                CompanyId=filterData['CompanyId'])
        if filterData['Status']:
            self.queryset = self.queryset.filter(Status=filterData['Status'])
        if Keyword:
            self.queryset = self.queryset.filter(StaffName__icontains=Keyword)

        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []
            for row in serializer.data:
                try:
                    designation = Designation.objects.get(
                        DesignationId=row['Designation'])
                    designationSerializer = DesignationSerializer(designation)
                    row['DesignationName'] = designationSerializer.data['Designation']
                except:
                    row['DesignationName'] = ""

                projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=row['StaffId'])
                projectTaskSerializer = ProjectTaskSerializer(
                    projectTask, many=True)
                work_status_count = {'Pending': 0, 'Completed': 0, 'Due': 0,
                                     'Not Completed': 0, 'Finished': 0, 'Delay Finished': 0}
                current_date = str(date.today())
                total_points_gain = 0
                count = 0
                for task in projectTaskSerializer.data:
                    if task['Status'] == '7' or task['Status'] == '8' or task['Status'] == '9':
                        total_points_gain = total_points_gain + \
                            float(task['CompletionPoint'])
                        count = count+1
                    if task['Status'] == '1' or task['Status'] == '2' or task['Status'] == '10':
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
                work_status_count['Performance'] = 0
                if count:

                    work_status_count['Performance'] = total_points_gain/count

                row['WorkStatusCount'] = work_status_count
                data.append(row)
            return self.get_paginated_response(data)
        # except:
        #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for Get all staff",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def StaffApiByCompanyId(request):
    try:
        if request.method == 'POST':
            filterData = JSONParser().parse(request)
            salarySlip = Staff.objects.filter(
                CompanyId=filterData['CompanyId'])
            salarySlipSerializer = StaffSerializer(
                salarySlip, many=True)
            return JsonResponse(salarySlipSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all SalarySlip Details",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def SalarySlipApi(request, StaffId="", Year="", Month=""):
    try:
        if request.method == 'GET':
            salarySlip = SalarySlip.objects.filter(
                StaffId=StaffId, Year=Year, Month=Month)
            salarySlipSerializer = SalarySlipSerializer(
                salarySlip)
            return JsonResponse(salarySlipSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all SalarySlip Details by staff id",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def GetSalarySlipByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET':
            salarySlip = SalarySlip.objects.filter(StaffId=StaffId)
            salarySlipSerializer = SalarySlipSerializer(
                salarySlip, many=True)
            return JsonResponse(salarySlipSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Create salary slip")
@api_view(['GET'])
@retry(retries=3, delay=2)
def CreateSalarySlipApi(request, CompanyId="", Year="", Month=""):
    # try:
    if request.method == 'GET':
        staffDa = Staff.objects.filter(Status=1, CompanyId=CompanyId)
        staffSerializer = StaffSerializer(
            staffDa, many=True)
        # return JsonResponse(staffSerializer.data, safe=False)

        today = datetime.today()
        if Year and Month:
            today = datetime.now().replace(year=int(Year), month=int(Month), day=1)
        first_day_of_this_month = today.replace(day=1)
        last_day_of_last_month = first_day_of_this_month - timedelta(days=1)
        last_month = last_day_of_last_month.month
        last_month_year = last_day_of_last_month.year
        days_in_last_month = calendar.monthrange(
            last_month_year, last_month)[1]

        # First day of last month
        first_day_of_last_month = last_day_of_last_month.replace(day=1)

        # Get the number of days in the last month
        days_in_last_month = calendar.monthrange(
            last_month_year, last_month)[1]

        # Formatting the dates
        first_day_str = str(first_day_of_last_month.strftime('%Y-%m-%d'))
        last_day_str = str(last_day_of_last_month.strftime('%Y-%m-%d'))
        for staff in staffSerializer.data:
            # try:
            first_day_time = datetime.fromisoformat(first_day_str)
            last_day_time = datetime.fromisoformat(last_day_str)
            joining_date = datetime.fromisoformat(staff['JoinedOn'])
            no_working_days = 0
            if first_day_time < joining_date:
                no_working_days = no_working_days + \
                    (joining_date - first_day_time).days+1
            if staff['LeavingDate'] is not None:
                try:
                    relieving_date = datetime.fromisoformat(
                        staff['LeavingDate'])
                    if last_day_time > relieving_date:
                        no_working_days = no_working_days + \
                            (last_day_time - relieving_date).days+1
                except:
                    p = 0
            total_working_days = days_in_last_month-no_working_days
            salary = float(staff['Salary'])
            start_date = timezone.datetime.strptime(
                first_day_str, '%Y-%m-%d').date()
            end_date = (timezone.datetime.strptime(
                last_day_str, '%Y-%m-%d') + timezone.timedelta(days=1)).date()
            leaveApplication = LeaveApplication.objects.filter(Q(LeaveFrom__range=(start_date, end_date)) | Q(
                LeaveTo__range=(start_date, end_date)), Status__in=[2], StaffId=staff['StaffId'])
            leaveApplicationSerializer = LeaveApplicationSerializer(
                leaveApplication, many=True)
            LOP = calculate_leave(
                leaveApplicationSerializer.data, last_month_year, last_month)
            PaidDays = total_working_days-LOP
            Leave = 0
            salaryPay = (float(salary)/float(days_in_last_month)*(PaidDays))
            BasicPay = salaryPay*.6
            ConveyanceAllowance = salaryPay*.1
            MedicalAllowance = salaryPay*.1
            OtherAllowance = salaryPay*.2
            AppreciationBonus = 0
            PerformancePoint = ProjectTask.objects.filter(Status__in=[7, 8, 9], TaskAssignedTo=staff['StaffId'], CreatedDate__range=(
                start_date, end_date), TaskType='Task').aggregate(average=Avg('TaskPoint'))['average']
            if PerformancePoint and float(PerformancePoint) >= 1.5:
                AppreciationBonus = (
                    (float(PerformancePoint)-float(1.5))*2)*(salaryPay*.1)

            GrossPay = salaryPay+AppreciationBonus
            # staffBankDetails=StaffBankDetails.objects.get(PrimaryAccount=1,StaffId=staff['StaffId'])
            # bankSerializer=StaffBankDetailsSerializer(staffBankDetails)

            data = {
                'SalarySlipId': '',
                'StaffId': staff['StaffId'],
                'Year': last_month_year,
                'Month': last_month,
                'BasicPay': round(BasicPay, 2),
                'ConveyanceAllowance': round(ConveyanceAllowance, 2),
                'MedicalAllowance': round(MedicalAllowance, 2),
                'OtherAllowance': round(OtherAllowance, 2),
                'AppreciationBonus': round(AppreciationBonus, 2),
                'TotalWorkingDays': total_working_days,
                'LOP': LOP,
                'PaidDays': PaidDays,
                'Leave': Leave,
                'GrossPay': round(GrossPay, 2),
                'BankAccount': staff['BankAccount'],
            }
            salarySlip = SalarySlipSerializer(
                data=data)
            if salarySlip.is_valid():
                salarySlip.save()

            # except:
            #     p=""
        return JsonResponse("staffSerializer.data", safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


def calculate_leave(leave_entries, target_year, target_month):

    total_leave_days = 0

    for entry in leave_entries:
        leave_type = entry['LeaveType']
        leave_from = datetime.fromisoformat(entry['LeaveFrom']) if isinstance(
            entry['LeaveFrom'], str) else entry['LeaveFrom']
        leave_to = datetime.fromisoformat(entry['LeaveTo']) if isinstance(
            entry['LeaveTo'], str) else entry['LeaveTo']

        # Calculate the start and end dates within July
        start_date = max(leave_from, datetime(target_year, target_month, 1))
        end_date = min(leave_to, datetime(
            target_year, target_month + 1, 1) - timedelta(days=1))

        # Calculate the number of leave days if there's an overlap
        if start_date <= end_date:
            if leave_type == '1' and start_date.month == target_month:
                total_leave_days += 0.5
            else:
                leave_days = (end_date - start_date).days + 1
                total_leave_days += leave_days

    return total_leave_days


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for download salary slip")
@api_view(['GET'])
def DownloadSalarySlip(request, Month, Year, StaffId):
    salarySlip = SalarySlip.objects.get(
        StaffId=StaffId, Year=Year, Month=Month)
    staffData = Staff.objects.get(StaffId=salarySlip.StaffId)
    try:
        companyData = Company.objects.get(CompanyId=staffData.CompanyId)
    except:
        companyData = ""

    TotalEarnings = salarySlip.BasicPay+salarySlip.ConveyanceAllowance + \
        salarySlip.MedicalAllowance+salarySlip.OtherAllowance+salarySlip.AppreciationBonus
    try:
        siteSettings = SiteSettings.objects.get(CompanyId=staffData.CompanyId)
        siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
        logo = os.path.join(settings.BASE_DIR) + \
            siteSettingsSerializer.data['Logo']
    except:
        logo = ""
    try:
        siteSettings = SiteSettings.objects.get(CompanyId=staffData.CompanyId)
        siteSettingsSerializer = SiteSettingsSerializer(siteSettings)
        companySeal = os.path.join(
            settings.BASE_DIR)+siteSettingsSerializer.data['CompanySeal']
    except:
        companySeal = ""
    try:
        designation = Designation.objects.get(
            DesignationId=staffData.Designation)
        designationSerializer = DesignationSerializer(designation)
        DesignationName = designationSerializer.data['Designation']
    except:
        DesignationName = ""
    try:
        staffBankDetails = StaffBankDetails.objects.get(
            PrimaryAccount=1, StaffId=StaffId)
        staffBankDetailsSerializer = StaffBankDetailsSerializer(
            staffBankDetails)
        bankDetails = staffBankDetailsSerializer.data
    except:
        bankDetails = ""

    TotalDeductions = 0
    NetSalary = TotalEarnings-TotalDeductions
    context = {
        'salarySlip': salarySlip,
        'staff': staffData,
        'JoinedDate': datetime.strptime(staffData.JoinedOn, '%Y-%m-%d').strftime('%B %d, %Y'),
        'company': companyData,
        'DesignationName': DesignationName,
        'TotalEarnings': TotalEarnings,
        'TotalDeductions': TotalDeductions,
        'NetSalary': NetSalary,
        'companySeal': companySeal,
        'logo': logo,
        'Month':  calendar.month_name[int(Month)],
        'Year': Year,
        'staffBankDetails': bankDetails
    }
    # return JsonResponse("", safe=False)
    pdf = render_to_pdf('salary_slip.html', context)
    response = HttpResponse(pdf.content, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="salary_slip_' + \
        staffData.StaffName+'_' + \
        calendar.month_name[int(Month)]+'_'+Year+'.pdf"'
    return response


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')

    return None


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for save salary slip")
@swagger_auto_schema(method='PUT', operation_description="NOTE: API for edit salary slip")
@api_view(['POST', 'PUT'])
@retry(retries=3, delay=2)
def CURDSalarySlipApi(request):
    try:
        if request.method == 'POST':
            salarySlipData = JSONParser().parse(request)
            salarySlipSerializer = SalarySlipSerializer(
                data=salarySlipData)
            if salarySlipSerializer.is_valid():
                salarySlipSerializer.save()
                return JsonResponse(salarySlipSerializer.data['SalarySlipId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            salarySlipData = JSONParser().parse(request)
            salarySlip = SalarySlip.objects.get(
                SalarySlipId=salarySlipData['SalarySlipId'])
            salarySlipSerializer = SalarySlipSerializer(
                salarySlip, data=salarySlipData)
            if salarySlipSerializer.is_valid():
                salarySlipSerializer.save()
                return JsonResponse(salarySlipSerializer.data['SalarySlipId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=MoveOnRegisterSerializer, operation_description="NOTE: API for save MoveOnRegister")
@swagger_auto_schema(method='PUT', request_body=MoveOnRegisterSerializer, operation_description="NOTE: API for edit MoveOnRegister")
@swagger_auto_schema(method='GET', operation_description="NOTE: Get all Move On Register Details",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def moveOnRegisterApi(request, StaffId=""):
    try:
        if request.method == 'GET':
            try:
                moveOnRegister = MoveOnRegister.objects.filter(
                    StaffId=StaffId).order_by('-SortId').first()
                moveOnRegister_serializer = MoveOnRegisterSerializer(
                    moveOnRegister)
                if moveOnRegister_serializer.data['StaffId']:
                    return JsonResponse(moveOnRegister_serializer.data, safe=False)
                return JsonResponse([], safe=False)
            except:
                return JsonResponse([], safe=False)
        elif request.method == 'POST':
            moveOnRegisterData = JSONParser().parse(request)
            # return JsonResponse(moveOnRegisterData, safe=False)
            moveOnRegisterSerializer = MoveOnRegisterSerializer(
                data=moveOnRegisterData)
            if moveOnRegisterSerializer.is_valid():
                moveOnRegisterSerializer.save()
                return JsonResponse(moveOnRegisterSerializer.data['MoveOnRegisterId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            moveOnRegisterData = JSONParser().parse(request)
            moveOnRegister = MoveOnRegister.objects.get(
                MoveOnRegisterId=moveOnRegisterData['MoveOnRegisterId'])
            moveOnRegisterSerializer = MoveOnRegisterSerializer(
                moveOnRegister, data=moveOnRegisterData)
            if moveOnRegisterSerializer.is_valid():
                moveOnRegisterSerializer.save()
                return JsonResponse(moveOnRegisterSerializer.data['MoveOnRegisterId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("Invalid request", safe=False)
    except:
        return JsonResponse("", safe=False)


# @csrf_exempt
# @swagger_auto_schema(method='GET',operation_description="NOTE: Get all Move On Register Details",)
# @api_view(['GET'])
# @retry(retries=3, delay=2)
# def StaffPerformanceByCompanyId(request,CompanyId=""):
#     try:
#         if request.method == 'GET':
#             data=AllStaffPerformancebyCompany(CompanyId)


#             return JsonResponse(data, safe=False)
#         else:
#             return JsonResponse("", safe=False)

#     except:
#         return JsonResponse("", safe=False)


def AllStaffPerformancebyCompany(CompanyId=""):
    staff = Staff.objects.filter(CompanyId=CompanyId)
    staffSerializer = StaffSerializer(staff, many=True)
    data = []
    for row in staffSerializer.data:
        try:
            designation = Designation.objects.get(
                DesignationId=row['Designation'])
            designationSerializer = DesignationSerializer(designation)
            row['DesignationName'] = designationSerializer.data['Designation']
        except:
            row['DesignationName'] = ""

        projectTask = ProjectTask.objects.filter(TaskAssignedTo=row['StaffId'])
        projectTaskSerializer = ProjectTaskSerializer(projectTask, many=True)
        work_status_count = {'Performance': 0}
        current_date = str(date.today())
        total_points_gain = 0
        count = 0
        Performance = 0
        for task in projectTaskSerializer.data:
            if task['Status'] == '7' or task['Status'] == '8' or task['Status'] == '9':
                total_points_gain = total_points_gain + \
                    float(task['CompletionPoint'])
                count = count+1

        if count:
            Performance = total_points_gain/count

        row['Performance'] = Performance
        data.append(row)
    return data


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get all project report. payload { StartDate, EndDate }")
@api_view(['GET'])
@retry(retries=3, delay=2)
def StaffPerformanceByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            currentMonthYear = date.today().strftime("%Y-%m")
            startDate = f"{currentMonthYear}-01"
            endDate = f"{currentMonthYear}-{date.today().strftime('%d')}"

            start_date = datetime.strptime(startDate, '%Y-%m-%d')
            end_date = datetime.strptime(endDate, '%Y-%m-%d')
            client = Staff.objects.filter(CompanyId=CompanyId)
            clientSerializer = StaffSerializer(client, many=True)
            projectData = []
            date_iter = start_date
            while date_iter <= end_date:
                total_points_gain = 0
                total_count = 0
                Performance = 0

                for row in clientSerializer.data:
                    task = ProjectTask.objects.annotate(
                        ScheduledDeadline_cast=Cast(
                            'ScheduledDeadline', DateTimeField())
                    ).filter(
                        ScheduledDeadline_cast__date=date_iter.date(),
                        TaskAssignedTo=row['StaffId']
                    )

                    taskSerializer = ProjectTaskSerializer(task, many=True)

                    for task in taskSerializer.data:
                        if task['Status'] in ['7', '8', '9']:
                            total_points_gain += float(task['CompletionPoint'])
                            total_count += 1

                Performance = total_points_gain / total_count if total_count > 0 else 0

                projectData.append({
                    'date': date_iter.strftime('%d'),
                    'overall_performance': Performance
                })

                date_iter += timedelta(days=1)

            return JsonResponse(projectData, safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=StaffBankDetailsSerializer, operation_description="NOTE: API for save StaffBankDetails")
@swagger_auto_schema(method='PUT', request_body=StaffBankDetailsSerializer, operation_description="NOTE: API for edit StaffBankDetails")
@api_view(['POST', 'PUT'])
@retry(retries=3, delay=2)
def StaffBankDetailsApi(request):
    # try:
    if request.method == 'POST':
        staffBankDetailsData = JSONParser().parse(request)
        staffBankDetailsSerializer = StaffBankDetailsSerializer(
            data=staffBankDetailsData)
        if staffBankDetailsData['PrimaryAccount'] == True:
            staffBankDetails = StaffBankDetails.objects.filter(
                PrimaryAccount=1, StaffId=staffBankDetailsData['StaffId'])
            for bank in staffBankDetails:
                bank.PrimaryAccount = False
                bank.save()
        if staffBankDetailsSerializer.is_valid():
            staffBankDetailsSerializer.save()
            staffBankDetails = StaffBankDetails.objects.filter(
                StaffId=staffBankDetailsData['StaffId'])
            if len(staffBankDetails) == 1:
                for row in staffBankDetails:
                    row.PrimaryAccount = True
                    row.save()

            return JsonResponse(staffBankDetailsSerializer.data['BankDetailId'], safe=False)
        return JsonResponse("Failed to add", safe=False)
    elif request.method == 'PUT':
        staffBankDetailsData = JSONParser().parse(request)
        staffBankDetails = StaffBankDetails.objects.get(
            BankDetailId=staffBankDetailsData['BankDetailId'])
        staffBankDetailsSerializer = StaffBankDetailsSerializer(
            staffBankDetails, data=staffBankDetailsData)
        if staffBankDetailsData['PrimaryAccount'] == True:
            staffBankDetails = StaffBankDetails.objects.filter(
                PrimaryAccount=1, StaffId=staffBankDetailsData['StaffId'])
            for bank in staffBankDetails:
                bank.PrimaryAccount = False
                bank.save()
        if staffBankDetailsSerializer.is_valid():
            staffBankDetailsSerializer.save()

            return JsonResponse(staffBankDetailsSerializer.data['BankDetailId'], safe=False)
        return JsonResponse("Failed to Update", safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get StaffBankDetails by StaffBankDetailsId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete StaffBankDetails by StaffBankDetailsId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def staffBankDetailsApiById(request, BankDetailId=""):
    try:
        if request.method == 'GET':
            staffBankDetails = StaffBankDetails.objects.get(
                BankDetailId=BankDetailId)
            staffBankDetailsSerializer = StaffBankDetailsSerializer(
                staffBankDetails)
            return JsonResponse(staffBankDetailsSerializer.data, safe=False)
        elif request.method == 'DELETE':
            staffBankDetails = StaffBankDetails.objects.get(
                BankDetailId=BankDetailId)
            staffBankDetails.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get StaffBankDetails by StaffId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def staffBankDetailsApiByStaffId(request, StaffId=""):
    try:
        if request.method == 'GET':
            staffBankDetails = StaffBankDetails.objects.filter(
                StaffId=StaffId)
            staffBankDetailsSerializer = StaffBankDetailsSerializer(
                staffBankDetails, many=True)
            return JsonResponse(staffBankDetailsSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)
