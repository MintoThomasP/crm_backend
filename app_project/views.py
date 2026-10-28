import uuid
import re
import base64
from django.core.files.base import ContentFile
import shutil
import os
from app_firebase.models import DeviceToken
from app_firebase.views import saveNotification, send_message_to_Token
from firebase_admin import messaging, initialize_app, credentials
from django.http import JsonResponse
from datetime import date
import json
import operator
from functools import reduce
from django.dispatch import receiver
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from app_basic.models import TempleteType
from app_basic.serializers import TempleteTypeSerializer
from io import BytesIO
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from app_client.serializers import ClientVisitRegisterSerializer
from app_client.models import Client, ClientAddress, ContactPerson
from app_company.models import Company
from app_company.serializers import CompanySerializer
from app_default.views import retry
from app_login.models import Login
from rest_framework.parsers import JSONParser
from app_default.models import TaskStatus
from app_default.serializers import TaskStatusSerializer
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from app_report.views import durationCalculation, pointCalculation
from app_site.serializers import NotificationSerializer
from app_staff.models import Staff
from datetime import datetime, time, timedelta
from app_staff.serializers import StaffSerializer
from rest_framework.pagination import PageNumberPagination
from app_project.models import CommentFile, Comments, Project, ProjectDocument, ProjectTask, ProjectTaskFile, ProjectTaskTiming, TaskReviews
from app_project.serializers import CommentFileSerializer, CommentsSerializer, ProjectDocumentSerializer, ProjectSerializer, ProjectTaskFileSerializer, ProjectTaskSerializer, ProjectTaskTimingSerializer,  SaveProjectTaskFileSerializer, TaskReviewsSerializer, UploadProjectTaskFileSerializer
from dateutil.relativedelta import relativedelta
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view
from django.utils import timezone
from datetime import datetime
import logging
from typing import Any, Dict
from uuid import uuid4
from django.conf import settings
from django.core.cache import cache
import firebase_admin
from firebase_admin import credentials
from app_staff.models import Staff
from rest_framework import generics
from django.db.models import Q


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 40  # Adjust the page size as needed
    page_size_query_param = 'page_size'


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectSerializer, operation_description="NOTE:API for save Project")
@swagger_auto_schema(method='PUT', request_body=ProjectSerializer, operation_description="NOTE:API for edit Project")
@swagger_auto_schema(method='GET', operation_description="NOTE:API for Get all Project Details by company id",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def ProjectApi(request, CompanyId=""):
    try:
        if request.method == 'GET':
            project = Project.objects.filter(
                CompanyId=CompanyId, ActiveStatus=1).order_by('-SortId')
            projectSerializer = ProjectSerializer(
                project, many=True)

            projectData = []
            for row in projectSerializer.data:
                projectTask = ProjectTask.objects.filter(
                    ProjectId=row['ProjectId'], TaskType="Task")
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
                projectData.append(row)

            return JsonResponse(projectData, safe=False)

        elif request.method == 'POST':
            projectData = JSONParser().parse(request)
            projectSerializer = ProjectSerializer(
                data=projectData)
            if projectSerializer.is_valid():
                projectSerializer.save()

                return JsonResponse(projectSerializer.data['ProjectId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectData = JSONParser().parse(request)
            project = Project.objects.get(
                ProjectId=projectData['ProjectId'])
            projectSerializer = ProjectSerializer(
                project, data=projectData)
            if projectSerializer.is_valid():
                projectSerializer.save()
                return JsonResponse(projectSerializer.data['ProjectId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Project by ProjectId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete Project by ProjectId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def ProjectApiById(request, ProjectId=""):
    try:
        if request.method == 'GET':
            project = Project.objects.get(
                ProjectId=ProjectId)
            projectSerializer = ProjectSerializer(
                project)
            return JsonResponse(projectSerializer.data, safe=False)
        elif request.method == 'DELETE':
            project = Project.objects.get(ProjectId=ProjectId)
            project.ActiveStatus = 0
            project.save()

            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class ProjectApiByCompanyId(generics.ListAPIView):
    queryset = Project.objects.filter(ActiveStatus=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(
                    CompanyId=filterData['CompanyId'])

            if Keyword:
                self.queryset = self.queryset.filter(
                    Q(ProjectName__icontains=Keyword) | Q(Description__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get project by CompanyId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectByCompanyId(request, CompanyId=""):
    try:
        if request.method == 'GET':
            project = Project.objects.filter(
                CompanyId=CompanyId, ActiveStatus=1)
            projectSerializer = ProjectSerializer(
                project, many=True)
            return JsonResponse(projectSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class ProjectTaskPagination(generics.ListAPIView):
    queryset = ProjectTask.objects.filter(Q(RefId__isnull=True) | Q(
        RefId=""), TaskType='Task').order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer

    def post(self, request, *args, **kwargs):
        # try:
        filterData = JSONParser().parse(request)
        Keyword = filterData.get('SearchKeyword', '')
        if len(filterData['TaskName']):
            self.queryset = self.queryset.filter(
                reduce(operator.or_, (Q(Title__icontains=task_name)
                       for task_name in filterData['TaskName']))
            )
        if len(filterData['TaskAssignedTo']):
            self.queryset = self.queryset.filter(
                TaskAssignedTo__in=filterData['TaskAssignedTo'])
        if filterData['CompanyId']:
            project = Project.objects.filter(
                CompanyId=filterData['CompanyId'], ActiveStatus=1)
            projectSerializer = ProjectSerializer(
                project, many=True)
            projectId = []
            for row in projectSerializer.data:
                projectId.append(row['ProjectId'])
            self.queryset = self.queryset.filter(ProjectId__in=projectId)
        if len(filterData['Status']):
            status = filterData['Status']
            self.queryset = self.queryset.filter(Status__in=status)
        if len(filterData['TaskAssignedBy']):
            self.queryset = self.queryset.filter(
                TaskAssignedBy__in=filterData['TaskAssignedBy'])
        if len(filterData['ProjectId']):
            self.queryset = self.queryset.filter(
                ProjectId__in=filterData['ProjectId'])
        if len(filterData['ClientId']):
            self.queryset = self.queryset.filter(
                ClientId__in=filterData['ClientId'])
        # if Keyword:
        #         self.queryset = self.queryset.filter(Q(Title__icontains=Keyword)|Q(Description__icontains=Keyword))
        if filterData['CreatedDate']:
            created_date_str = filterData['CreatedDate']
            created_date = datetime.strptime(
                created_date_str, '%Y-%m-%d').date()
            self.queryset = self.queryset.filter(
                CreatedDate__startswith=created_date)
        if filterData['EndDate']:
            end_date_str = filterData['EndDate']
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            self.queryset = self.queryset.filter(EndDate__startswith=end_date)

        if filterData.get('FromDate'):
            # Convert FromDate to start of the day in ScheduledDeadline's format
            from_date_str = datetime.strptime(
                filterData['FromDate'], '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M')
        else:
            from_date_str = None

        if filterData.get('ToDate'):
            # Convert ToDate to end of the day in ScheduledDeadline's format
            to_date = datetime.strptime(
                filterData['ToDate'], '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
            to_date_str = to_date.strftime('%Y-%m-%dT%H:%M')
        else:
            to_date_str = None

        # Apply string-based filtering
        if from_date_str and to_date_str:
            self.queryset = self.queryset.filter(
                ScheduledDeadline__gte=from_date_str, ScheduledDeadline__lte=to_date_str)
        elif from_date_str:
            self.queryset = self.queryset.filter(
                ScheduledDeadline__gte=from_date_str)
        elif to_date_str:
            self.queryset = self.queryset.filter(
                ScheduledDeadline__lte=to_date_str)

        # return JsonResponse(str(self.queryset.query), safe=False)
        page = self.paginate_queryset(self.queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = []

            for row in serializer.data:

                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId'], TaskType='Ticket').order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    row['Tickets'] = projectTaskSerializer.data[0]
                except:
                    row['Tickets'] = []
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId'], TaskType='Subtask').order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    subTasks = []
                    for subtask in projectTaskSerializer.data:
                        try:
                            taskStatus = TaskStatus.objects.get(
                                StatusId=subtask['Status'])
                            taskStatusSerializer = TaskStatusSerializer(
                                taskStatus)
                            subtask['StatusName'] = taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName'] = ""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] = []

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    row['AssignedTo'] = staffSerializer.data['StaffName']
                except:
                    row['AssignedTo'] = ""

                try:
                    try:
                        staff = Staff.objects.get(
                            StaffId=row['TaskAssignedBy'])
                        staffSerializer = StaffSerializer(staff)
                        row['AssignedBy'] = staffSerializer.data['StaffName']
                    except:
                        company = Company.objects.get(
                            CompanyId=row['TaskAssignedBy'])
                        companySerializer = CompanySerializer(company)
                        row['AssignedBy'] = companySerializer.data['CompanyName']
                except:
                    row['AssignedBy'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                data.append(row)
            return self.get_paginated_response(data)
        # except:
        #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Rest Task Point",)
@api_view(['GET'])
def RestTaskPoint(request):
    projectTask = ProjectTask.objects.filter(TaskType="Task")
    projectTaskSerializer = ProjectTaskSerializer(
        projectTask, many=True)
    success = 0
    failed = 0
    data_return = []
    for projectTask in projectTaskSerializer.data:
        # if projectTask['TotalDuration'] is None:

        projectTaskTiming = ProjectTaskTiming.objects.filter(
            ProjectTaskId=projectTask['ProjectTaskId'])
        projectTaskTimingSerializer = ProjectTaskTimingSerializer(
            projectTaskTiming, many=True)
        total_duration_minutes = 0
        if len(projectTaskTimingSerializer.data):
            for row in projectTaskTimingSerializer.data:

                try:
                    date_format = '%Y-%m-%dT%H:%M:%S.%f'
                    start_date = datetime.strptime(
                        row['StartDate'], date_format)
                    end_date = datetime.strptime(row['EndDate'], date_format)
                except:
                    date_format = '%Y-%m-%dT%H:%M:%S.%f'
                    try:
                        start_date = datetime.strptime(
                            projectTask['StartDate'], date_format)
                    except:
                        try:
                            hours, minutes = map(
                                int, projectTask['Duration'].split(':'))
                        except:
                            projectTask['Duration'] = "0:10"
                        duration = timedelta(hours=1, minutes=0)
                        try:
                            ScheduledDeadline = datetime.strptime(
                                projectTask['ScheduledDeadline'], date_format)
                            start_date = ScheduledDeadline + duration
                        except:
                            ScheduledDeadline = datetime.strptime(
                                projectTask['SortId'], date_format)
                            start_date = ScheduledDeadline + duration

                        formatted_datetime = start_date.strftime(
                            '%Y-%m-%dT%H:%M:%S%z')
                        projectTask['StartDate'] = formatted_datetime[:-
                                                                      2] + ':' + formatted_datetime[-2:]
                    try:
                        end_date = datetime.strptime(
                            projectTask['EndDate'], date_format)
                    except:
                        hours, minutes = map(
                            int, projectTask['Duration'].split(':'))
                        duration = timedelta(hours=1, minutes=0)
                        end_date = start_date + duration
                        formatted_datetime = end_date.strftime(
                            '%Y-%m-%dT%H:%M:%S%z')
                        projectTask['EndDate'] = formatted_datetime[:-
                                                                    2] + ':' + formatted_datetime[-2:]

                total_time_taken = end_date - start_date
                total_time_taken_in_seconds = total_time_taken.total_seconds()
                total_time_taken_data = {
                    'hours': round(total_time_taken_in_seconds // 3600),
                    'minutes': round((total_time_taken_in_seconds % 3600) // 60)
                }
                duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
                row['Duration'] = duration
                # row.save()

                hours, minutes = map(int, duration.split(':'))
                total_duration_minutes += hours * 60 + minutes

            total_duration_hours = total_duration_minutes // 60
            total_duration_remaining_minutes = total_duration_minutes % 60
            total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

            projectTask['TotalDuration'] = total_duration
        else:
            date_format = '%Y-%m-%dT%H:%M:%S.%f'
            try:
                start_date = datetime.strptime(
                    projectTask['StartDate'], date_format)
            except:
                try:
                    hours, minutes = map(
                        int, projectTask['Duration'].split(':'))
                except:
                    projectTask['Duration'] = "0:10"
                duration = timedelta(hours=1, minutes=0)
                try:
                    ScheduledDeadline = datetime.strptime(
                        projectTask['ScheduledDeadline'], date_format)
                    start_date = ScheduledDeadline + duration
                except:
                    ScheduledDeadline = datetime.strptime(
                        projectTask['SortId'], date_format)
                    start_date = ScheduledDeadline + duration

                formatted_datetime = start_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                projectTask['StartDate'] = formatted_datetime[:-
                                                              2] + ':' + formatted_datetime[-2:]
            try:
                end_date = datetime.strptime(
                    projectTask['EndDate'], date_format)
            except:
                hours, minutes = map(int, projectTask['Duration'].split(':'))
                duration = timedelta(hours=1, minutes=0)
                end_date = start_date + duration
                formatted_datetime = end_date.strftime('%Y-%m-%dT%H:%M:%S%z')
                projectTask['EndDate'] = formatted_datetime[:-2] + \
                    ':' + formatted_datetime[-2:]
            total_time_taken = end_date - start_date
            total_time_taken_in_seconds = total_time_taken.total_seconds()
            total_time_taken_data = {
                'hours': round(total_time_taken_in_seconds // 3600),
                'minutes': round((total_time_taken_in_seconds % 3600) // 60)
            }
            duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
            projectTask['TotalDuration'] = duration
        projectTask['CompletionPoint'] = round(
            float(pointCalculation(projectTask)), 2)
        projectTaskLive = ProjectTask.objects.get(
            ProjectTaskId=projectTask['ProjectTaskId'])
        projectTaskSerializerLive = ProjectTaskSerializer(
            projectTaskLive, data=projectTask)

        data_return.append(projectTask)
        # if projectTaskSerializerLive.is_valid():
        #     success=success+1
        #     projectTaskSerializerLive.save()

        # else:
        #     failed=failed+1

    return JsonResponse(data_return, safe=False)


@csrf_exempt
def DeleteTaskByAdmin(request):
    if request.method == 'POST':
        request_data = JSONParser().parse(request)

        project = Project.objects.filter(
            CompanyId=request_data['CompanyId'])
        projectSerializer = ProjectSerializer(
            project, many=True)
        projectId = []
        for row in projectSerializer.data:
            projectId.append(row['ProjectId'])
        projectTasks = ProjectTask.objects.filter(
            IsTemplate=0, ProjectId__in=projectId
        )

        for task in projectTasks:
            # Delete related files
            projectTaskFiles = ProjectTaskFile.objects.filter(
                ProjectTaskId=task.ProjectTaskId)
            for file in projectTaskFiles:
                if file.TaskFile:
                    file.TaskFile.delete(save=True)
                file.delete()

            # Delete related timing entries
            projectTaskTimings = ProjectTaskTiming.objects.filter(
                ProjectTaskId=task.ProjectTaskId)
            for timing in projectTaskTimings:
                timing.delete()

            # Delete the task itself
            task.delete()

        return JsonResponse({'status': 'success', 'message': 'Tasks deleted successfully'})


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectTaskSerializer, operation_description="NOTE: API for save ProjectTask")
@swagger_auto_schema(method='PUT', request_body=ProjectTaskSerializer, operation_description="NOTE: API for edit ProjectTask")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all ProjectTask",)
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def ProjectTaskApi(request):
    # try:
    if request.method == 'GET':
        projectTask = ProjectTask.objects.filter(
            Q(RefId__isnull=True) | Q(RefId=""), TaskType='Task').order_by('-SortId')
        projectTaskSerializer = ProjectTaskSerializer(
            projectTask, many=True)
        taskData = []
        for row in projectTaskSerializer.data:
            row['Tickets'] = []
            try:
                projectTask = ProjectTask.objects.get(
                    RefId=row['ProjectTaskId'])
                projectTaskSerializer = ProjectTaskSerializer(projectTask)
                row['Tickets'] = projectTaskSerializer.data
            except:
                row['Tickets'] = []

            try:
                project = Project.objects.get(ProjectId=row['ProjectId'])
                projectSerializer = ProjectSerializer(project)
                row['ProjectName'] = projectSerializer.data['ProjectName']
            except:
                row['ProjectName'] = ""
            try:
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['AssignedTo'] = staffSerializer.data['StaffName']
            except:
                row['AssignedTo'] = ""

            try:
                staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                staffSerializer = StaffSerializer(staff)
                row['AssignedBy'] = staffSerializer.data['StaffName']
            except:
                row['AssignedBy'] = ""

            try:
                staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                staffSerializer = StaffSerializer(staff)
                row['VerifiedByName'] = staffSerializer.data['StaffName']
            except:
                row['VerifiedByName'] = ""
            try:
                taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                taskStatusSerializer = TaskStatusSerializer(taskStatus)
                row['StatusName'] = taskStatusSerializer.data['Status']
            except:
                row['StatusName'] = ""
            try:
                projectTaskFile = ProjectTaskFile.objects.filter(
                    ProjectTaskId=row['ProjectTaskId'])
                projectTaskFileSerializer = ProjectTaskFileSerializer(
                    projectTaskFile, many=True)
                row['ProjectTaskFiles'] = projectTaskFileSerializer.data
            except:
                row['ProjectTaskFiles'] = ""

            taskData.append(row)

        return JsonResponse(taskData, safe=False)
    elif request.method == 'POST':
        projectTaskData = JSONParser().parse(request)
        projectTaskSerializer = ProjectTaskSerializer(
            data=projectTaskData)
        if projectTaskSerializer.is_valid():
            projectTaskSerializer.save()

            if projectTaskSerializer.data['IsRepeated'] == 1:
                RepeatInterval = projectTaskSerializer.data['RepeatInterval']
                Interval = projectTaskSerializer.data['Interval']
                next_Scheduled_date = calculateNextScheduledDate(
                    RepeatInterval, Interval, projectTaskData['ScheduledOn'])

                projectTask = ProjectTask.objects.get(
                    ProjectTaskId=projectTaskSerializer.data['ProjectTaskId'])
                projectTask.NextScheduledDate = next_Scheduled_date
                projectTask.save()

            if projectTaskSerializer.data['TaskType'] == "Task" or projectTaskSerializer.data['TaskType'] == "Ticket":
                try:
                    # login = Login.objects.get(
                    #     UserId=projectTaskSerializer.data['TaskAssignedTo'])
                    # if login.Token:
                    title = "New task added"
                    if projectTaskSerializer.data['TaskType'] == "Ticket":
                        title = "New ticket raised"
                    staff = Staff.objects.get(
                        StaffId=projectTaskSerializer.data['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    sendNotification({
                        "title": title,
                        "body": projectTaskSerializer.data['Title'],
                        # "token": login.Token,
                        "fromuser": projectTaskSerializer.data['TaskAssignedBy'],
                        "touser": projectTaskSerializer.data['TaskAssignedTo'],
                        "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                        "notification_type": "Task",
                        "id": projectTaskSerializer.data['ProjectTaskId']
                    })

                except:
                    p = ""

            return JsonResponse(projectTaskSerializer.data['ProjectTaskId'], safe=False)
        return JsonResponse("Failed to add", safe=False)
    elif request.method == 'PUT':
        projectTaskData = JSONParser().parse(request)
        projectTask = ProjectTask.objects.get(
            ProjectTaskId=projectTaskData['ProjectTaskId'])
        projectTaskSerializer = ProjectTaskSerializer(
            projectTask, data=projectTaskData)
        if projectTaskSerializer.is_valid():
            projectTaskSerializer.save()
            if projectTaskSerializer.data['IsRepeated'] == 1:
                RepeatInterval = projectTaskSerializer.data['RepeatInterval']
                Interval = projectTaskSerializer.data['Interval']
                next_Scheduled_date = calculateNextScheduledDate(
                    RepeatInterval, Interval)
                projectScheduleDate = ProjectTask.objects.get(
                    ProjectTaskId=projectTaskData['ProjectTaskId'])
                projectScheduleDate.NextScheduledDate = next_Scheduled_date
                projectScheduleDate.save()
            if projectTaskSerializer.data['TaskType'] != 'Subtask' and projectTaskSerializer.data['TaskType'] != 'Ticket':
                if projectTaskData['Status'] == '7' or projectTaskData['Status'] == '8' or projectTaskData['Status'] == '9' or projectTaskData['Status'] == 7 or projectTaskData['Status'] == 8 or projectTaskData['Status'] == 9:
                    projectTaskPoint = ProjectTask.objects.get(
                        ProjectTaskId=projectTaskData['ProjectTaskId'])
                    projectTaskPoint.CompletionPoint = pointCalculation(
                        projectTaskSerializer.data)
                    projectTaskPoint.save()
                if projectTaskSerializer.data['Status'] == '3':
                    # login = Login.objects.get(
                    #     UserId=projectTaskSerializer.data['TaskAssignedBy'])
                    title = "Need verification"
                    if projectTaskSerializer.data['TaskType'] == "Ticket":
                        title = "Ticket closed"
                    # if login.Token:

                    staff = Staff.objects.get(
                        StaffId=projectTaskSerializer.data['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    sendNotification({
                        "title": title,
                        "body": projectTaskSerializer.data['Title'],
                        # "token": login.Token,
                        "fromuser": projectTaskSerializer.data['TaskAssignedTo'],
                        "touser": projectTaskSerializer.data['TaskAssignedBy'],
                        "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                        "notification_type": "Task",
                        "id": projectTaskSerializer.data['ProjectTaskId']
                    })
                elif projectTaskSerializer.data['Status'] == '4' or projectTaskSerializer.data['Status'] == '5' or projectTaskSerializer.data['Status'] == '6':
                    # login = Login.objects.get(
                    #     UserId=projectTaskSerializer.data['TaskAssignedTo'])
                    # if login.Token:
                    staff = Staff.objects.get(
                        StaffId=projectTaskSerializer.data['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    sendNotification({
                        "title": title,
                        "body": projectTaskSerializer.data['Title'],
                        # "token": login.Token,
                        "fromuser": projectTaskSerializer.data['TaskAssignedBy'],
                        "touser": projectTaskSerializer.data['TaskAssignedTo'],
                        "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                        "notification_type": "Task",
                        "id": projectTaskSerializer.data['ProjectTaskId']
                    })
                elif projectTaskSerializer.data['Status'] == '7' or projectTaskSerializer.data['Status'] == '8' or projectTaskSerializer.data['Status'] == '9':
                    if projectTaskSerializer.data['ClientId']:
                        payload = {
                            "ClientVisitRegisterId": "",
                            "ClientId": projectTaskSerializer.data['ClientId'],
                            "StaffId": projectTaskSerializer.data['TaskAssignedTo'],
                            "VisitedDate": projectTaskSerializer.data['EndDate'],
                            "Notes": "",
                        }
                        clientVisitRegisterSerializer = ClientVisitRegisterSerializer(
                            data=payload)
                        if clientVisitRegisterSerializer.is_valid():
                            clientVisitRegisterSerializer.save()
                    # login = Login.objects.get(
                    #     UserId=projectTaskSerializer.data['TaskAssignedTo'])
                    # if login.Token:
                    staff = Staff.objects.get(
                        StaffId=projectTaskSerializer.data['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    sendNotification({
                        "title": "Verified",
                        "body": projectTaskSerializer.data['Title'],
                        # "token": login.Token,
                        "fromuser": projectTaskSerializer.data['TaskAssignedBy'],
                        "touser": projectTaskSerializer.data['TaskAssignedTo'],
                        "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                        "notification_type": "Task",
                        "id": projectTaskSerializer.data['ProjectTaskId']
                    })

            return JsonResponse(projectTaskSerializer.data['ProjectTaskId'], safe=False)

        return JsonResponse("", safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectTask by ProjectTaskId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete ProjectTask by ProjectTaskId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def ProjectTaskApiById(request, ProjectTaskId=""):
    # try:
    if request.method == 'GET':
        projectTask = ProjectTask.objects.get(
            ProjectTaskId=ProjectTaskId)
        projectTaskSerializer = ProjectTaskSerializer(
            projectTask)
        ProjectTaskData = projectTaskSerializer.data
        try:
            projectSubTask = ProjectTask.objects.filter(
                RefId=ProjectTaskId, TaskType='Subtask').order_by('-SortId')
            projectSubTaskSerializer = ProjectTaskSerializer(
                projectSubTask, many=True)
            ProjectTaskData['SubTask'] = projectSubTaskSerializer.data
        except:
            ProjectTaskData['SubTask'] = []
        try:
            taskStatus = TaskStatus.objects.get(
                StatusId=projectTaskSerializer.data['Status'])
            taskStatusSerializer = TaskStatusSerializer(taskStatus)
            ProjectTaskData['StatusName'] = taskStatusSerializer.data['Status']
        except:
            ProjectTaskData['StatusName'] = ""
        ProjectTaskData['Tickets'] = []
        try:
            tickets = ProjectTask.objects.filter(
                RefId=ProjectTaskId, TaskType='Ticket').order_by('-SortId')
            ticketSerializer = ProjectTaskSerializer(tickets, many=True)
            ProjectTaskData['Tickets'] = ticketSerializer.data[0]
        except:
            ProjectTaskData['Tickets'] = []

        try:
            project = Project.objects.get(
                ProjectId=projectTaskSerializer.data['ProjectId'])
            projectSerializer = ProjectSerializer(project)
            ProjectTaskData['ProjectName'] = projectSerializer.data['ProjectName']
        except:
            ProjectTaskData['ProjectName'] = ""
        try:
            try:
                staff = Staff.objects.get(
                    StaffId=projectTaskSerializer.data['TaskAssignedBy'])
                staffSerializer = StaffSerializer(staff)
                ProjectTaskData['AssignedBy'] = staffSerializer.data['StaffName']
            except:
                company = Company.objects.get(
                    CompanyId=projectTaskSerializer.data['TaskAssignedBy'])
                companySerializer = CompanySerializer(company)
                ProjectTaskData['AssignedBy'] = companySerializer.data['CompanyName']
        except:
            ProjectTaskData['AssignedBy'] = ""

        try:
            staff = Staff.objects.get(
                StaffId=projectTaskSerializer.data['TaskAssignedTo'])
            staffSerializer = StaffSerializer(staff)
            ProjectTaskData['AssignedTo'] = staffSerializer.data['StaffName']
        except:
            ProjectTaskData['AssignedTo'] = ""

        try:
            staff = Staff.objects.get(
                StaffId=projectTaskSerializer.data['VerifiedBy'])
            staffSerializer = StaffSerializer(staff)
            ProjectTaskData['VerifiedByName'] = staffSerializer.data['StaffName']
        except:
            ProjectTaskData['VerifiedByName'] = ""
        try:
            projectTaskFile = ProjectTaskFile.objects.filter(
                ProjectTaskId=projectTaskSerializer.data['ProjectTaskId'])
            projectTaskFileSerializer = ProjectTaskFileSerializer(
                projectTaskFile, many=True)
            ProjectTaskData['ProjectTaskFiles'] = projectTaskFileSerializer.data
        except:
            ProjectTaskData['ProjectTaskFiles'] = ""
        try:
            comment = Comments.objects.filter(
                ProjectTaskId=ProjectTaskId).order_by('SortId')
            commentSerializer = CommentsSerializer(comment, many=True)
            commentData = []
            for fileSer in commentSerializer.data:
                commentFile = CommentFile.objects.filter(
                    CommentId=fileSer['CommentId'])
                commentFileSerializer = CommentFileSerializer(
                    commentFile, many=True)
                fileSer['CommentFiles'] = commentFileSerializer.data
                commentData.append(fileSer)
            ProjectTaskData['Comments'] = commentData

        except:
            ProjectTaskData['Comments'] = []
        return JsonResponse(ProjectTaskData, safe=False)
    elif request.method == 'DELETE':
        projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
        try:
            ProjectTask.objects.filter(
                RefId=ProjectTaskId, TaskType='Subtask').delete()
        except:
            p = ""
        try:
            ProjectTaskTiming.objects.filter(
                ProjectTaskId=ProjectTaskId).delete()
        except:
            p = ""
        try:
            taskFile = ProjectTaskFile.objects.filter(
                ProjectTaskId=ProjectTaskId)
            projectTaskSerializer = ProjectTaskFileSerializer(
                taskFile, many=True)
            for row in projectTaskSerializer.data:
                project_task_file_obj = ProjectTaskFile.objects.get(
                    ProjectTaskFileId=row['ProjectTaskFileId'])
                project_task_file_obj.TaskFile.delete(save=True)
                project_task_file_obj.delete()
        except:
            p = ""
        try:
            TaskReviews.objects.filter(ProjectTaskId=ProjectTaskId).delete()
        except:
            p = ""
        try:
            Comments.objects.filter(ProjectTaskId=ProjectTaskId).delete()
        except:
            p = ""
        projectTask.delete()
        return JsonResponse("Deleted successfully", safe=False)
    else:
        return JsonResponse("", safe=False)
    # except:
    #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectTask by ProjectId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskApiByProjectId(request, ProjectId=""):
    try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.filter(
                ProjectId=ProjectId).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                try:
                    projectsubTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectsubTaskSerializer = ProjectTaskSerializer(
                        projectsubTask, many=True)
                    row['SubTask'] = projectsubTaskSerializer.data
                except:
                    row['SubTask'] = []
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""

                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get My Task",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskApiByUserId(request, TaskAssignedTo=""):
    try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.filter(
                Q(TaskAssignedTo=TaskAssignedTo) &
                Q(TaskType='Task') |
                (Q(TaskType='Ticket') & Q(TaskAssignedTo=TaskAssignedTo)
                 & (Q(Status='2') | Q(Status='1')))
            ).order_by('-SortId')

            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:

                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    subTasks = []
                    for subtask in projectTaskSerializer.data:
                        try:
                            taskStatus = TaskStatus.objects.get(
                                StatusId=subtask['Status'])
                            taskStatusSerializer = TaskStatusSerializer(
                                taskStatus)
                            subtask['StatusName'] = taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName'] = ""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] = []

                row['Tickets'] = []
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    row['Tickets'] = projectTaskSerializer.data[0]
                except:
                    row['Tickets'] = []

                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

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
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)

            return JsonResponse(taskStatusName, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Task Assigned by me",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskApiByTaskAssignedBy(request, TaskAssignedBy=""):
    try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.filter(
                TaskAssignedBy=TaskAssignedBy, TaskType='Task').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:

                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    subTasks = []
                    for subtask in projectTaskSerializer.data:
                        try:
                            taskStatus = TaskStatus.objects.get(
                                StatusId=subtask['Status'])
                            taskStatusSerializer = TaskStatusSerializer(
                                taskStatus)
                            subtask['StatusName'] = taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName'] = ""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] = []
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

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
                    row['StaffName'] = []
                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""

                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)

            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectTaskSerializer, operation_description="NOTE: API for get ProjectTask by TaskAssignedTo and ProjectId. paylaod { ProjectId, TaskAssignedTo}",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiByUserIdAndProjectId(request):
    try:
        if request.method == 'POST':
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                ProjectId=projectTaskData['ProjectId'], TaskAssignedTo=projectTaskData['TaskAssignedTo']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                row['Tickets'] = []
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    row['SubTask'] = projectTaskSerializer.data
                except:
                    row['SubTask'] = []
                try:
                    projectTask = ProjectTask.objects.get(
                        RefId=row['ProjectTaskId'])
                    projectTaskSerializer = ProjectTaskSerializer(projectTask)
                    row['Tickets'] = projectTaskSerializer.data
                except:
                    row['Tickets'] = []
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']
                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""

                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""
                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectTaskSerializer, operation_description="NOTE: API for get ProjectTask by ProjectId and TaskAssignedBy. payload { ProjectId,TaskAssignedBy}",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiByTaskAssignedByAndProjectId(request):
    try:
        if request.method == 'POST':
            projectTaskData = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                ProjectId=projectTaskData['ProjectId'], TaskAssignedBy=projectTaskData['TaskAssignedBy']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskData = []
            for row in projectTaskSerializer.data:
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    row['SubTask'] = projectTaskSerializer.data
                except:
                    row['SubTask'] = []
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['StaffName'] = staffSerializer.data['StaffName']
                except:
                    row['StaffName'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskData.append(row)
            return JsonResponse(taskData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=TaskReviewsSerializer, operation_description="NOTE: API for save TaskReviews")
@swagger_auto_schema(method='PUT', request_body=TaskReviewsSerializer, operation_description="NOTE: API for edit TaskReviews")
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all task reviews")
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def TaskReviewsApi(request):
    try:
        if request.method == 'GET':
            taskReview = TaskReviews.objects.all().order_by('-SortId')
            taskReviewSerializer = TaskReviewsSerializer(
                taskReview, many=True)
            return JsonResponse(taskReviewSerializer.data, safe=False)
        elif request.method == 'POST':
            taskReviewData = JSONParser().parse(request)
            taskReviewSerializer = TaskReviewsSerializer(
                data=taskReviewData)
            if taskReviewSerializer.is_valid():
                taskReviewSerializer.save()

                return JsonResponse(taskReviewSerializer.data['TaskReviewId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            taskReviewData = JSONParser().parse(request)
            taskReview = TaskReviews.objects.get(
                TaskReviewId=taskReviewData['TaskReviewId'])
            taskReviewSerializer = TaskReviewsSerializer(
                taskReview, data=taskReviewData)
            if taskReviewSerializer.is_valid():
                taskReviewSerializer.save()
                return JsonResponse(taskReviewSerializer.data['TaskReviewId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get TaskReviews by TaskReviewId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete TaskReviews by TaskReviewId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def TaskReviewsApiById(request, TaskReviewId=""):
    try:
        if request.method == 'GET':
            taskReview = TaskReviews.objects.get(
                TaskReviewId=TaskReviewId)
            taskReviewSerializer = TaskReviewsSerializer(
                taskReview)
            return JsonResponse(taskReviewSerializer.data, safe=False)
        elif request.method == 'DELETE':
            taskReview = TaskReviews.objects.get(TaskReviewId=TaskReviewId)
            taskReview.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get all task by status. payload { StatusId}",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetAllTasksStatus(request):
    try:
        if request.method == 'POST':
            Statusdata = JSONParser().parse(request)
            projectTask = ProjectTask.objects.filter(
                Status=Statusdata['StatusId']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            return JsonResponse(projectTaskSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for Get all project Task file",)
@swagger_auto_schema(method='PUT', request_body=SaveProjectTaskFileSerializer, operation_description="NOTE: API for edit ProjectTaskFile")
@swagger_auto_schema(method='POST', request_body=SaveProjectTaskFileSerializer, operation_description="NOTE: API for save ProjectTaskFile")
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def ProjectTaskFileApi(request, pk=""):
    try:
        if request.method == 'GET':
            projectTaskFile = ProjectTaskFile.objects.all()
            projectTaskFileSerializer = ProjectTaskFileSerializer(
                projectTaskFile, many=True)
            return JsonResponse(projectTaskFileSerializer.data, safe=False)
        elif request.method == 'POST':
            projectTaskFile = JSONParser().parse(request)
            projectTaskFileSerializer = SaveProjectTaskFileSerializer(
                data=projectTaskFile)
            if projectTaskFileSerializer.is_valid():
                projectTaskFileSerializer.save()
                return JsonResponse(projectTaskFileSerializer.data['ProjectTaskFileId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectTaskFiledata = JSONParser().parse(request)
            projectTaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=projectTaskFiledata['ProjectTaskFileId'])
            projectTaskFileSerializer = SaveProjectTaskFileSerializer(
                projectTaskFile, data=projectTaskFiledata)
            if projectTaskFileSerializer.is_valid():
                projectTaskFileSerializer.save()
                return JsonResponse(projectTaskFileSerializer.data['ProjectTaskFileId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectTaskFile by ProjectTaskFileId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete ProjectTaskFile by ProjectTaskFileId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def CURDprojectTaskFileApiById(request, ProjectTaskFileId=""):
    try:
        if request.method == 'GET':
            projectTaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=ProjectTaskFileId)
            projectTaskFileSerializer = ProjectTaskFileSerializer(
                projectTaskFile)
            return JsonResponse(projectTaskFileSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectTaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=ProjectTaskFileId)
            ProjectTaskFile.objects.get(
                ProjectTaskFileId=ProjectTaskFileId).TaskFile.delete(save=True)
            projectTaskFile.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class UploadProjectTaskFile(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, ProjectTaskFileId="", *args, **kwargs):
        try:
            projectTaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=ProjectTaskFileId)
            try:
                ProjectTaskFile.objects.get(
                    ProjectTaskFileId=ProjectTaskFileId).TaskFile.delete(save=True)
            except:
                p = ""
            Serializer = UploadProjectTaskFileSerializer(
                projectTaskFile, data=request.data)
            if Serializer.is_valid():
                Serializer.save()
                return JsonResponse("ok", safe=False)
            else:
                return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get all comments",)
@swagger_auto_schema(method='PUT', request_body=CommentsSerializer, operation_description="NOTE: API for edit comments")
@swagger_auto_schema(method='POST', request_body=CommentsSerializer, operation_description="NOTE: API for save comments")
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def CommentApi(request, pk=""):
    try:
        if request.method == 'GET':
            comment = Comments.objects.all()
            commentSerializer = CommentsSerializer(
                comment, many=True)
            return JsonResponse(commentSerializer.data, safe=False)
        elif request.method == 'POST':
            comment = JSONParser().parse(request)
            commentSerializer = CommentsSerializer(
                data=comment)

            if commentSerializer.is_valid():
                commentSerializer.save()
                task = ProjectTask.objects.get(
                    ProjectTaskId=commentSerializer.data['ProjectTaskId'])
                try:
                    if comment['ShowNotification']:
                        if task.TaskAssignedBy != commentSerializer.data['CommentedBy'] and task.TaskAssignedTo == commentSerializer.data['CommentedBy']:
                            # login = Login.objects.get(
                            #     UserId=task.TaskAssignedBy)
                            # if login.Token:
                            staff = Staff.objects.get(
                                StaffId=commentSerializer.data['CommentedBy'])
                            staffSerializer = StaffSerializer(staff)
                            sendNotification({
                                "title": "Comments",
                                "body": commentSerializer.data['Comment'],
                                # "token": login.Token,
                                "fromuser": commentSerializer.data['CommentedBy'],
                                "touser": task.TaskAssignedBy,
                                "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                                "notification_type": "Comment",
                                "id": ""
                            })

                        elif task.TaskAssignedBy == commentSerializer.data['CommentedBy'] and task.TaskAssignedTo != commentSerializer.data['CommentedBy']:
                            # login = Login.objects.get(
                            #     UserId=task.TaskAssignedTo)
                            # if login.Token:
                            staff = Staff.objects.get(
                                StaffId=commentSerializer.data['CommentedBy'])
                            staffSerializer = StaffSerializer(staff)
                            sendNotification({
                                "title": "Comments",
                                "body": commentSerializer.data['Comment'],
                                # "token": login.Token,
                                "fromuser": commentSerializer.data['CommentedBy'],
                                "touser": task.TaskAssignedTo,
                                "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                                "notification_type": "Comment",
                                "id": ""
                            })
                        else:

                            staff = Staff.objects.get(
                                StaffId=commentSerializer.data['CommentedBy'])
                            staffSerializer = StaffSerializer(staff)
                            sendNotification({
                                "title": "Comments",
                                "body": commentSerializer.data['Comment'],
                                # "token": login.Token,
                                "fromuser": commentSerializer.data['CommentedBy'],
                                "touser": task.TaskAssignedTo,
                                "icon": "https://crm-api-live.cubexizsoft.com"+staffSerializer.data['ProfilePhoto'],
                                "notification_type": "Comment",
                                "id": ""
                            })
                except:
                    p = ""

                return JsonResponse(commentSerializer.data['CommentId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            commentdata = JSONParser().parse(request)
            comment = Comments.objects.get(
                CommentId=commentdata['CommentId'])
            commentSerializer = CommentsSerializer(
                comment, data=commentdata)
            if commentSerializer.is_valid():
                commentSerializer.save()
                return JsonResponse(commentSerializer.data['CommentId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get comments by CommentId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete comments by CommentId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def CURDCommentApiById(request, CommentId=""):
    try:
        if request.method == 'GET':
            comment = Comments.objects.get(
                CommentId=CommentId)
            commentSerializer = CommentsSerializer(
                comment)
            return JsonResponse(commentSerializer.data, safe=False)
        elif request.method == 'DELETE':
            comment = Comments.objects.get(CommentId=CommentId)
            comment.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE:API for Get all Comment File",)
@swagger_auto_schema(method='PUT', request_body=CommentFileSerializer, operation_description="NOTE:API for edit CommentFile")
@swagger_auto_schema(method='POST', request_body=CommentFileSerializer, operation_description="NOTE:API for save CommentFile")
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def CommentFileApi(request, pk=""):
    try:
        if request.method == 'GET':
            commentFile = CommentFile.objects.all()
            commentFileSerializer = CommentFileSerializer(
                commentFile, many=True)
            return JsonResponse(commentFileSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get CommentFile by CommentFileId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete CommentFile by CommentFileId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def CURDCommentFileApiById(request, CommentFileId=""):
    try:
        if request.method == 'GET':
            commentFile = CommentFile.objects.get(
                CommentFileId=CommentFileId)
            commentFileSerializer = CommentFileSerializer(
                commentFile)
            return JsonResponse(commentFileSerializer.data, safe=False)
        elif request.method == 'DELETE':
            commentFile = CommentFile.objects.get(CommentFileId=CommentFileId)
            commentFile.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class UploadCommentFile(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request,  *args, **kwargs):
        try:
            Serializer = CommentFileSerializer(
                data=request.data)
            if Serializer.is_valid():
                Serializer.save()
                return JsonResponse(Serializer.data['CommentFileId'], safe=False)
            else:
                return JsonResponse("", safe=False)
        except:
            return JsonResponse("", safe=False)


@swagger_auto_schema(method='POST', operation_description="NOTE: API for Filtering ProjectTask by TaskAssignedTo. payload {CreatedDate,Status,ProjectId,TaskAssignedTo }",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiFilteringforTaskAssignedTo(request,):
    try:
        if request.method == 'POST':
            taskData = JSONParser().parse(request)
            if taskData['CreatedDate'] and taskData['Status'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, ProjectId=taskData['ProjectId'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['Status'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate']:
                CreatedDate = timezone.datetime.strptime(
                    CreatedDate, '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['Status']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    ProjectId=taskData['ProjectId'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            else:
                projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:

                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for Filtering ProjectTask by TaskAssignedBy. payload {CreatedDate,Status,ProjectId,TaskAssignedBy }",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def ProjectTaskApiFilteringforTaskAssignedBy(request,):
    try:
        if request.method == 'POST':
            taskData = JSONParser().parse(request)
            if taskData['CreatedDate'] and taskData['Status'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status'], TaskAssignedBy=taskData['TaskAssignedBy'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status'], TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, ProjectId=taskData['ProjectId'], TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['Status'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], TaskAssignedBy=taskData['TaskAssignedBy'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate']:
                CreatedDate = timezone.datetime.strptime(
                    CreatedDate, '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['Status']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            elif taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    ProjectId=taskData['ProjectId'], TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            else:
                projectTask = ProjectTask.objects.filter(
                    TaskAssignedBy=taskData['TaskAssignedBy']).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:

                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                staffSerializer = StaffSerializer(staff)
                row['StaffName'] = staffSerializer.data['StaffName']

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)
            return JsonResponse(taskStatusName, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@swagger_auto_schema(method='POST', operation_description="NOTE: API for Filtering all ProjectTask. payload {CreatedDate,Status,ProjectId,TaskAssignedTo }",)
@api_view(['POST'])
@retry(retries=3, delay=2)
def GetAllProjectTaskApiByFiltering(request):
    try:
        if request.method == 'POST':
            taskData = JSONParser().parse(request)

            if taskData['CreatedDate'] and taskData['Status'] and taskData['TaskAssignedTo'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, ProjectId=taskData['ProjectId'], Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['TaskAssignedTo'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, TaskAssignedTo=taskData['TaskAssignedTo'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['Status'] and taskData['TaskAssignedTo'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status'] and taskData['TaskAssignedTo']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['Status']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, Status=taskData['Status']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['TaskAssignedTo']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['CreatedDate'] and taskData['ProjectId']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate, ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['TaskAssignedTo'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=taskData['TaskAssignedTo'], ProjectId=taskData['ProjectId']).order_by('-SortId')

            elif taskData['Status'] and taskData['TaskAssignedTo']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['Status'] and taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status'], ProjectId=taskData['ProjectId']).order_by('-SortId')
            elif taskData['Status']:
                projectTask = ProjectTask.objects.filter(
                    Status=taskData['Status']).order_by('-SortId')
            elif taskData['CreatedDate']:
                CreatedDate = timezone.datetime.strptime(
                    taskData['CreatedDate'], '%Y-%m-%d').date()
                projectTask = ProjectTask.objects.filter(
                    CreatedDate=CreatedDate).order_by('-SortId')
            elif taskData['TaskAssignedTo']:
                projectTask = ProjectTask.objects.filter(
                    TaskAssignedTo=taskData['TaskAssignedTo']).order_by('-SortId')
            elif taskData['ProjectId']:
                projectTask = ProjectTask.objects.filter(
                    ProjectId=taskData['ProjectId']).order_by('-SortId')
            else:
                projectTask = ProjectTask.objects.all().order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskData = []
            for row in projectTaskSerializer.data:
                try:
                    project = Project.objects.get(ProjectId=row['ProjectId'])
                    projectSerializer = ProjectSerializer(project)
                    row['ProjectName'] = projectSerializer.data['ProjectName']
                except:
                    row['ProjectName'] = ""
                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedTo'])
                    staffSerializer = StaffSerializer(staff)
                    row['AssignedTo'] = staffSerializer.data['StaffName']
                except:
                    row['AssignedTo'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['TaskAssignedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['AssignedBy'] = staffSerializer.data['StaffName']
                except:
                    row['AssignedBy'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskData.append(row)

            return JsonResponse(taskData, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@swagger_auto_schema(method='GET', operation_description="NOTE: API for Auto schedule repeated task",)
@api_view(['GET'])
def schedule_repeated_tasks(request):

    retries = 3
    for _ in range(retries):
        try:
            now = timezone.now()
            repeated_tasks = ProjectTask.objects.filter(IsRepeated=True)
            projectTaskSerializer = ProjectTaskSerializer(
                repeated_tasks, many=True)

            data = []
            i = 0
            for task in repeated_tasks:
                given_date = datetime.now()
                day_of_week = int((given_date.weekday() + 1))

                next_Schduled_date = None
                scheduled_deadline = None

                currentDate = given_date.strftime("%Y-%m-%d")
                currentScheduledDate = task.NextScheduledDate.strftime(
                    "%Y-%m-%d")

                if task.RepeatInterval == 'daily' and currentDate == currentScheduledDate:

                    interval = task.Interval
                    if day_of_week == 7:
                        interval = interval+1
                        next_Schduled_date = now + timedelta(days=interval)

                        scheduled_deadline = next_Schduled_date + \
                            timedelta(days=interval)

                    else:
                        next_Schduled_date = now + timedelta(days=interval)
                        scheduled_deadline = next_Schduled_date + \
                            timedelta(days=interval)

                elif task.RepeatInterval == 'weekly' and currentDate == currentScheduledDate:

                    interval = task.Interval
                    if day_of_week == 7:
                        interval = interval+1
                        next_Schduled_date = now + timedelta(weeks=interval)
                        scheduled_deadline = next_Schduled_date + \
                            timedelta(weeks=interval)
                    else:
                        next_Schduled_date = now + timedelta(weeks=interval)
                        scheduled_deadline = next_Schduled_date + \
                            timedelta(weeks=interval)

                elif task.RepeatInterval == 'monthly' and currentDate == currentScheduledDate:

                    interval = task.Interval
                    if day_of_week == 7:
                        interval = interval+1
                        next_Schduled_date = now + \
                            relativedelta(months=interval)
                        scheduled_deadline = next_Schduled_date + \
                            relativedelta(months=interval)
                    else:
                        next_Schduled_date = now + \
                            relativedelta(months=interval)
                        scheduled_deadline = next_Schduled_date + \
                            relativedelta(months=interval)

                elif task.RepeatInterval == 'yearly' and currentDate == currentScheduledDate:
                    interval = task.Interval
                    if day_of_week == 7:
                        interval = interval+1
                        next_Schduled_date = now + \
                            relativedelta(years=interval)
                        scheduled_deadline = next_Schduled_date + \
                            relativedelta(years=interval)
                    else:
                        next_Schduled_date = now + \
                            relativedelta(years=interval)
                        scheduled_deadline = next_Schduled_date + \
                            relativedelta(years=interval)

                if currentDate == currentScheduledDate and (task.RepeatInterval == 'daily' or task.RepeatInterval == 'weekly' or task.RepeatInterval == 'monthly'):

                    new_task = {
                        "ProjectId": task.ProjectId,
                        "TaskAssignedTo": task.TaskAssignedTo,
                        "TaskAssignedBy": task.TaskAssignedBy,
                        "Title": task.Title,
                        "Description": task.Description,
                        "Duration": task.Duration,
                        "Status": 1,
                        "CreatedDate": given_date.strftime("%Y-%m-%dT%H:%M:%S%z"),
                        "ScheduledDeadline": scheduled_deadline.strftime("%Y-%m-%dT%H:%M"),
                        "TaskPoint": task.TaskPoint,
                        "TaskType": task.TaskType,
                        "RefId": task.RefId,
                        "NextScheduledDate": next_Schduled_date,
                        "Interval": task.Interval,
                        "ClientId": task.ClientId,
                        "IsRepeated": True,
                        "RepeatInterval": task.RepeatInterval

                    }

                    new_taskserializer = ProjectTaskSerializer(data=new_task)

                    if new_taskserializer.is_valid():
                        new_taskserializer.save()
                        subtasks = ProjectTask.objects.filter(
                            RefId=task.ProjectTaskId)
                        subtaskSerializer = ProjectTaskSerializer(
                            subtasks, many=True)
                        for subtask in subtaskSerializer.data:
                            new_subtask_data = {
                                "ProjectId": subtask['ProjectId'],
                                "TaskAssignedTo": subtask['TaskAssignedTo'],
                                "TaskAssignedBy": subtask['TaskAssignedBy'],
                                "Title": subtask['Title'],
                                "Description": subtask['Description'],
                                "Status": 1,
                                "CreatedDate": given_date,
                                "ScheduledDeadline": scheduled_deadline,
                                "TaskPoint": subtask['TaskPoint'],
                                "TaskType": subtask['TaskType'],
                                "RefId": new_taskserializer.data['ProjectTaskId']

                            }
                            new_subtaskserializer = ProjectTaskSerializer(
                                data=new_subtask_data)
                            if new_subtaskserializer.is_valid():
                                new_subtaskserializer.save()
                            else:
                                print(new_subtaskserializer.errors)

                        i = i+1
                        data.append(new_taskserializer.data)

            return JsonResponse({"message": "Repeated tasks scheduled successfully.", "data": data, "projectTaskSerializer": projectTaskSerializer.data, "count": i}, safe=False)
        except NotImplementedError as e:
            return JsonResponse({"error": "NotImplementedError occurred"}, status=500)


# from django_q.tasks import schedule
# from django_q.models import Schedule
# from datetime import timedelta
# from django.utils import timezone

# schedule('app_project.views.schedule_repeated_tasks',
#          schedule_type=Schedule.MINUTES,
#          minutes=2,  # Adjust as necessary
#          next_run=timezone.now() + timedelta(seconds=10))


# # path to credentials.json file
# cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)


# firebase_app = firebase_admin.initialize_app(cred, name='app_project')


# # Initialize the Firebase app (you only need to do this once)
# cred = credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
# initialize_app(cred)


def sendNotification(notifyData):

    data = {
        "icon": notifyData['icon'],
        "notification_type": notifyData['notification_type'],
        "id": notifyData['id']
    }

    Tokens = DeviceToken.objects.filter(
        UserId=notifyData['touser'], Active=True).values_list('Token', flat=True)
    if Tokens:
        for Token in Tokens:
            send_message_to_Token(
                Token,
                notifyData['title'],
                notifyData['body'],
                data)
    saveNotification(
        notifyData['fromuser'],
        notifyData['touser'],
        notifyData['title'],
        notifyData['body'],
        data)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get all Project task timing")
@swagger_auto_schema(method='PUT', request_body=ProjectTaskTimingSerializer, operation_description="NOTE: API for save ProjectTaskTiming")
@swagger_auto_schema(method='POST', request_body=ProjectTaskTimingSerializer, operation_description="NOTE: API for edit ProjectTaskTiming")
@api_view(['GET', 'POST', 'PUT'])
@retry(retries=3, delay=2)
def ProjectTaskTimingApi(request, pk=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.all()
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming, many=True)
            return JsonResponse(projectTaskTimingSerializer.data, safe=False)
        elif request.method == 'POST':
            projectTaskTiming = JSONParser().parse(request)
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                data=projectTaskTiming)
            if projectTaskTimingSerializer.is_valid():
                projectTaskTimingSerializer.save()
                return JsonResponse(projectTaskTimingSerializer.data['ProjectTaskTimingId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectTaskTimingdata = JSONParser().parse(request)
            projectTaskTiming = ProjectTaskTiming.objects.get(
                ProjectTaskTimingId=projectTaskTimingdata['ProjectTaskTimingId'])
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming, data=projectTaskTimingdata)
            if projectTaskTimingSerializer.is_valid():
                projectTaskTimingSerializer.save()
                ProjectTaskId = projectTaskTimingSerializer.data['ProjectTaskId']
                ProjectTaskTimingCalculationById(ProjectTaskId)
                projectTask = ProjectTask.objects.get(
                    ProjectTaskId=projectTaskTiming.ProjectTaskId)
                projectTask.EndDate = projectTaskTimingdata['EndDate']
                projectTask.save()

                return JsonResponse(projectTaskTimingSerializer.data['ProjectTaskTimingId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectTaskTiming by ProjectTaskTimingId",)
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete ProjectTaskTiming by ProjectTaskTimingId",)
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def CURDprojectTaskTimingApiById(request, ProjectTaskTimingId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.get(
                ProjectTaskTimingId=ProjectTaskTimingId)
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming)
            return JsonResponse(projectTaskTimingSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectTaskTiming = ProjectTaskTiming.objects.get(
                ProjectTaskTimingId=ProjectTaskTimingId)
            projectTaskTiming.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectTaskTiming by ProjectTaskId",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectTaskTimingApiByProjectTaskId(request, ProjectTaskId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.filter(
                ProjectTaskId=ProjectTaskId)
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming, many=True)
            return JsonResponse(projectTaskTimingSerializer.data, safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get LastTiming of a task",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def getLastTimmingByTaskId(request, ProjectTaskId=""):
    try:
        if request.method == 'GET':
            projectTaskTiming = ProjectTaskTiming.objects.filter(Q(Q(EndDate__isnull=True) | Q(
                EndDate='')) & Q(ProjectTaskId=ProjectTaskId)).order_by('-SortId')
            projectTaskTimingSerializer = ProjectTaskTimingSerializer(
                projectTaskTiming, many=True)
            return JsonResponse(projectTaskTimingSerializer.data[0], safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


def ProjectTaskTimingCalculationById(ProjectTaskId=""):
    # TaskTiming = ProjectTaskTiming.objects.get(ProjectTaskTimingId=ProjectTaskTimingId)
    projectTaskTiming = ProjectTaskTiming.objects.filter(
        ProjectTaskId=ProjectTaskId)
    projectTaskTimingSerializer = ProjectTaskTimingSerializer(
        projectTaskTiming, many=True)
    total_duration_minutes = 0
    for row in projectTaskTiming:
        date_format = '%Y-%m-%dT%H:%M:%S%z'
        start_date = datetime.strptime(row.StartDate, date_format)
        end_date = datetime.strptime(row.EndDate, date_format)

        total_time_taken = end_date - start_date
        total_time_taken_in_seconds = total_time_taken.total_seconds()
        total_time_taken_data = {
            'hours': round(total_time_taken_in_seconds // 3600),
            'minutes': round((total_time_taken_in_seconds % 3600) // 60)
        }
        duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
        row.Duration = duration
        row.save()

        hours, minutes = map(int, duration.split(':'))
        total_duration_minutes += hours * 60 + minutes

    total_duration_hours = total_duration_minutes // 60
    total_duration_remaining_minutes = total_duration_minutes % 60
    total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

    projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
    projectTask.TotalDuration = total_duration
    projectTask.save()


# @csrf_exempt
# @swagger_auto_schema(method='GET', operation_description="",)
# @api_view(['GET'])
# @retry(retries=3, delay=2)
# def ProjectTaskTotalDurationCalculation(request):
#     if request.method == 'GET':
#         projectTask = ProjectTask.objects.all()
#         projectTaskTimingSerializer = ProjectTaskSerializer(projectTask, many=True)
#         total_duration_minutes = 0

#         for row in projectTask:
#             if row.StartDate and row.EndDate:
#                 date_formats = [
#                     '%m/%d/%Y, %I:%M:%S %p',  # Example: 04/07/2024, 10:06:38 AM
#                     '%m/%d/%Y, %H:%M:%S',     # Example: 04/07/2024, 10:06:38
#                     '%d/%m/%Y, %I:%M:%S %p',  # Example: 07/04/2024, 10:06:38 AM
#                     '%d/%m/%Y, %H:%M:%S',     # Example: 07/04/2024, 10:06:38,
#                     "%Y-%m-%dT%H:%M:%S%z"
#                 ]

#                 start_date = end_date = None
#                 for date_format in date_formats:
#                     try:
#                         start_date = datetime.strptime(row.StartDate, date_format)
#                         end_date = datetime.strptime(row.EndDate, date_format)
#                         break
#                     except ValueError:
#                         continue

#                 if start_date and end_date:
#                     total_time_taken = end_date - start_date
#                     total_time_taken_in_seconds = total_time_taken.total_seconds()
#                     total_time_taken_data = {
#                         'hours': int(total_time_taken_in_seconds // 3600),
#                         'minutes': int((total_time_taken_in_seconds % 3600) // 60)
#                     }
#                     duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']:02}"
#                     row.TotalDuration = duration
#                     row.save()

#         return JsonResponse("Updated", safe=False)


class GetAllTicketsApi(generics.ListAPIView):
    queryset = ProjectTask.objects.filter(
        TaskType='Ticket').order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                project = Project.objects.filter(
                    CompanyId=filterData['CompanyId'], ActiveStatus=1)
                projectSerializer = ProjectSerializer(
                    project, many=True)
                projectId = []
                for row in projectSerializer.data:
                    projectId.append(row['ProjectId'])
                self.queryset = self.queryset.filter(ProjectId__in=projectId)
            if len(filterData['TaskAssignedTo']):
                self.queryset = self.queryset.filter(
                    TaskAssignedTo__in=filterData['TaskAssignedTo'])
            if len(filterData['TaskAssignedBy']):
                self.queryset = self.queryset.filter(
                    TaskAssignedBy__in=filterData['TaskAssignedBy'])
            if len(filterData['ProjectId']):
                self.queryset = self.queryset.filter(
                    ProjectId__in=filterData['ProjectId'])
            if filterData.get('FromDate'):
                # Convert FromDate to start of the day in ScheduledDeadline's format
                from_date_str = datetime.strptime(
                    filterData['FromDate'], '%Y-%m-%d').strftime('%Y-%m-%dT%H:%M')
            else:
                from_date_str = None

            if filterData.get('ToDate'):
                # Convert ToDate to end of the day in ScheduledDeadline's format
                to_date = datetime.strptime(
                    filterData['ToDate'], '%Y-%m-%d') + timedelta(days=1) - timedelta(seconds=1)
                to_date_str = to_date.strftime('%Y-%m-%dT%H:%M')
            else:
                to_date_str = None

            # Apply string-based filtering
            if from_date_str and to_date_str:
                self.queryset = self.queryset.filter(
                    CreatedDate__gte=from_date_str, CreatedDate__lte=to_date_str)
            elif from_date_str:
                self.queryset = self.queryset.filter(
                    CreatedDate__gte=from_date_str)
            elif to_date_str:
                self.queryset = self.queryset.filter(
                    CreatedDatee__lte=to_date_str)

            # Filter by Status
            if filterData['Status']:
                status = filterData['Status']
                if isinstance(status, int):
                    status = [status]
                self.queryset = self.queryset.filter(Status__in=status)
            # if filterData['Status']:
            #     status=filterData['Status']
            #     self.queryset = self.queryset.filter(Status__in=status)
            # if Keyword:
            #         self.queryset = self.queryset.filter(Q(Title__icontains=Keyword)|Q(Description__icontains=Keyword))
            # if filterData['CreatedDate']:
            #     created_date_str = filterData['CreatedDate']
            #     created_date = datetime.strptime(created_date_str, '%Y-%m-%d').date()
            #     self.queryset = self.queryset.filter(CreatedDate__startswith=created_date)

            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    row['Tickets'] = []
                    try:
                        projectTask = ProjectTask.objects.get(
                            RefId=row['ProjectTaskId'])
                        projectTaskSerializer = ProjectTaskSerializer(
                            projectTask)
                        row['Tickets'] = projectTaskSerializer.data
                    except:
                        row['Tickets'] = []
                    try:
                        project = Project.objects.get(
                            ProjectId=row['ProjectId'])
                        projectSerializer = ProjectSerializer(project)
                        row['ProjectName'] = projectSerializer.data['ProjectName']
                    except:
                        row['ProjectName'] = ""
                    try:
                        staff = Staff.objects.get(
                            StaffId=row['TaskAssignedTo'])
                        staffSerializer = StaffSerializer(staff)
                        row['AssignedTo'] = staffSerializer.data['StaffName']
                    except:
                        row['AssignedTo'] = ""

                    try:
                        staff = Staff.objects.get(
                            StaffId=row['TaskAssignedBy'])
                        staffSerializer = StaffSerializer(staff)
                        row['AssignedBy'] = staffSerializer.data['StaffName']
                    except:
                        row['AssignedBy'] = ""

                    try:
                        staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                        staffSerializer = StaffSerializer(staff)
                        row['VerifiedByName'] = staffSerializer.data['StaffName']
                    except:
                        row['VerifiedByName'] = ""
                    try:
                        taskStatus = TaskStatus.objects.get(
                            StatusId=row['Status'])
                        taskStatusSerializer = TaskStatusSerializer(taskStatus)
                        row['StatusName'] = taskStatusSerializer.data['Status']
                    except:
                        row['StatusName'] = ""

                    try:
                        projectTaskFile = ProjectTaskFile.objects.filter(
                            ProjectTaskId=row['ProjectTaskId'])
                        projectTaskFileSerializer = ProjectTaskFileSerializer(
                            projectTaskFile, many=True)
                        row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                    except:
                        row['ProjectTaskFiles'] = ""

                    data.append(row)

                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Tickets by TaskAssignedTo",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def TicketsByTaskAssignedTo(request, TaskAssignedTo=""):
    try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.filter(
                TaskAssignedTo=TaskAssignedTo, TaskType='Ticket').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                row['Tickets'] = []
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    row['Tickets'] = projectTaskSerializer.data[0]
                except:
                    row['Tickets'] = []

                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

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
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)
            MediaViewData = []
            batch_size = 50
            for start in range(0, len(taskStatusName), batch_size):
                batch = taskStatusName[start:start + batch_size]
                for media in batch:
                    MediaViewData.append(media)

            return JsonResponse(MediaViewData, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get Tickets by TaskAssignedBy",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def TicketsByTaskAssignedBy(request, TaskAssignedBy=""):
    try:
        if request.method == 'GET':
            projectTask = ProjectTask.objects.filter(
                TaskAssignedBy=TaskAssignedBy, TaskType='Ticket').order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                row['Tickets'] = []
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId']).order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    row['Tickets'] = projectTaskSerializer.data[0]
                except:
                    row['Tickets'] = []

                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

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
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)
            MediaViewData = []
            batch_size = 50
            for start in range(0, len(taskStatusName), batch_size):
                batch = taskStatusName[start:start + batch_size]
                for media in batch:
                    MediaViewData.append(media)

            return JsonResponse(MediaViewData, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


def calculateNextScheduledDate(RepeatInterval="", Interval="", date=""):

    if date:
        given_date = datetime.fromisoformat(date)
    else:
        given_date = datetime.now()
    day_of_week = int((given_date.weekday() + 1))
    now = timezone.now()
    if RepeatInterval == 'daily':
        interval = Interval
        if day_of_week == 7:
            interval = interval+1
            next_Schduled_date = now + timedelta(days=interval)

        else:
            next_Schduled_date = now + timedelta(days=interval)

    elif RepeatInterval == 'weekly':
        interval = Interval
        if day_of_week == 7:
            interval = interval+1
            next_Schduled_date = now + timedelta(weeks=interval)

        else:
            next_Schduled_date = now + timedelta(weeks=interval)

    elif RepeatInterval == 'monthly':

        interval = Interval
        if day_of_week == 7:
            interval = interval+1
            next_Schduled_date = now + relativedelta(months=interval)

        else:
            next_Schduled_date = now + relativedelta(months=interval)

    elif RepeatInterval == 'yearly':
        interval = Interval
        if day_of_week == 7:
            interval = interval+1
            next_Schduled_date = now + relativedelta(years=interval)

        else:
            next_Schduled_date = now + relativedelta(years=interval)
    return next_Schduled_date


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get My Task",)
@api_view(['GET'])
@retry(retries=3, delay=2)
def GetallTaskTemplate(request, CompanyId=""):
    try:
        if request.method == 'GET':
            # project = Project.objects.filter(
            #             CompanyId=CompanyId)
            # projectSerializer = ProjectSerializer(
            #         project,many=True)
            # projectId=[]
            # for row in projectSerializer.data:
            #     projectId.append(row['ProjectId'])

            projectTask = ProjectTask.objects.filter(
                IsTemplate=1, CompanyId=CompanyId).order_by('-SortId')
            projectTaskSerializer = ProjectTaskSerializer(
                projectTask, many=True)
            taskStatusName = []
            for row in projectTaskSerializer.data:
                try:
                    projectTask = ProjectTask.objects.filter(
                        RefId=row['ProjectTaskId'], TaskType='Subtask').order_by('-SortId')
                    projectTaskSerializer = ProjectTaskSerializer(
                        projectTask, many=True)
                    subTasks = []
                    for subtask in projectTaskSerializer.data:
                        try:
                            taskStatus = TaskStatus.objects.get(
                                StatusId=subtask['Status'])
                            taskStatusSerializer = TaskStatusSerializer(
                                taskStatus)
                            subtask['StatusName'] = taskStatusSerializer.data['Status']
                        except:
                            subtask['StatusName'] = ""
                        subTasks.append(subtask)

                    row['SubTask'] = subTasks
                except:
                    row['SubTask'] = []

                try:
                    taskStatus = TaskStatus.objects.get(StatusId=row['Status'])
                    taskStatusSerializer = TaskStatusSerializer(taskStatus)
                    row['StatusName'] = taskStatusSerializer.data['Status']
                except:
                    row['StatusName'] = ""

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
                    row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                except:
                    row['TaskAssignedByName'] = ""

                try:
                    staff = Staff.objects.get(StaffId=row['VerifiedBy'])
                    staffSerializer = StaffSerializer(staff)
                    row['VerifiedByName'] = staffSerializer.data['StaffName']
                except:
                    row['VerifiedByName'] = ""
                try:
                    projectTaskFile = ProjectTaskFile.objects.filter(
                        ProjectTaskId=row['ProjectTaskId'])
                    projectTaskFileSerializer = ProjectTaskFileSerializer(
                        projectTaskFile, many=True)
                    row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                except:
                    row['ProjectTaskFiles'] = ""

                taskStatusName.append(row)

            return JsonResponse(taskStatusName, safe=False)

        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class GetAllTemplatesByPagination(generics.ListAPIView):
    queryset = ProjectTask.objects.filter(IsTemplate=1).order_by('-SortId')
    pagination_class = CustomPageNumberPagination
    serializer_class = ProjectTaskSerializer

    def post(self, request, *args, **kwargs):
        try:
            filterData = JSONParser().parse(request)
            Keyword = filterData.get('SearchKeyword', '')
            if filterData['CompanyId']:
                self.queryset = self.queryset.filter(
                    CompanyId=filterData['CompanyId'])
            if Keyword:
                self.queryset = self.queryset.filter(
                    Q(Title__icontains=Keyword) | Q(Description__icontains=Keyword))
            page = self.paginate_queryset(self.queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                data = []

                for row in serializer.data:
                    try:
                        taskStatus = TaskStatus.objects.get(
                            StatusId=row['Status'])
                        taskStatusSerializer = TaskStatusSerializer(taskStatus)
                        row['StatusName'] = taskStatusSerializer.data['Status']
                    except:
                        row['StatusName'] = ""
                    try:
                        templateType = TempleteType.objects.get(
                            TempleteTypeId=row['TempleteType'])
                        templateTypeSerializer = TempleteTypeSerializer(
                            templateType)
                        row['TempleteTypeName'] = templateTypeSerializer.data['TempleteType']
                    except:
                        row['TempleteTypeName'] = ""

                    try:
                        try:
                            staff = Staff.objects.get(
                                StaffId=row['TaskAssignedBy'])
                            staffSerializer = StaffSerializer(staff)
                            row['TaskAssignedByName'] = staffSerializer.data['StaffName']
                        except:
                            company = Company.objects.get(
                                CompanyId=row['TaskAssignedBy'])
                            companySerializer = CompanySerializer(company)
                            row['TaskAssignedByName'] = companySerializer.data['CompanyName']
                    except:
                        row['TaskAssignedByName'] = ""

                    try:
                        projectTaskFile = ProjectTaskFile.objects.filter(
                            ProjectTaskId=row['ProjectTaskId'])
                        projectTaskFileSerializer = ProjectTaskFileSerializer(
                            projectTaskFile, many=True)
                        row['ProjectTaskFiles'] = projectTaskFileSerializer.data
                    except:
                        row['ProjectTaskFiles'] = ""
                    data.append(row)
                return self.get_paginated_response(data)
        except:
            return JsonResponse("", safe=False)


# class SaveProjectTaskFile(APIView):
#     parser_classes = (MultiPartParser, FormParser)
#     def post(self, request,  *args, **kwargs):
#         # try:
#                 Serializer = SaveProjectTaskFileSerializer(
#                     data=request.data)
#                 if Serializer.is_valid():
#                     Serializer.save()
#                     return JsonResponse(Serializer.data['ProjectTaskFileId'], safe=False)
#                 else:
#                     return JsonResponse("", safe=False)
#         # except:
#         #     return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get My Task")
@api_view(['GET'])
def copy_image(request, ProjectTaskFileId=""):
    try:

        projecttaskFile = ProjectTaskFile.objects.get(
            ProjectTaskFileId=ProjectTaskFileId)
        source_relative_path = projecttaskFile.TaskFile.name

        source_path = os.path.join(settings.MEDIA_ROOT, source_relative_path)

        destination_folder = os.path.join(settings.MEDIA_ROOT, 'Template')
        # destination_path = os.path.join(destination_folder, 'image.jpg')
        destination_path = os.path.join(
            destination_folder, os.path.basename(source_relative_path))

        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.copy2(source_path, destination_path)

        return JsonResponse(destination_path, safe=False)

    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API for get My Task")
@api_view(['POST'])
def savecopy_image(request,):
    try:
        if request.method == 'POST':
            projectdata = JSONParser().parse(request)
            projecttaskFile = ProjectTaskFile.objects.get(
                ProjectTaskFileId=projectdata['ProjectTaskFileId'])

            if 'TaskFile' in projectdata:
                image_data = projectdata['TaskFile']

                if isinstance(image_data, str) and image_data.startswith('data:image'):

                    format, imgstr = image_data.split(';base64,')
                    ext = format.split('/')[-1]
                    image_data = ContentFile(base64.b64decode(
                        imgstr), name=f"{uuid.uuid4()}.{ext}")

                projecttaskFile.TaskFile = image_data
                projecttaskFile.save()
                return JsonResponse("updated", safe=False)

            return JsonResponse("TaskFile not provided", safe=False)

    except ProjectTaskFile.DoesNotExist:
        return JsonResponse("ProjectTaskFile not found", safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, safe=False)


@csrf_exempt
@api_view(['GET'])
@retry(retries=3, delay=2)
def UpdateClientandCompanyInTask(request):
    try:
        if request.method == 'GET':
            project = Project.objects.all()
            projectSerializer = ProjectSerializer(project, many=True)
            for row in projectSerializer.data:
                company_id = row['CompanyId']
                client_id = row['ClientId']
                projectTask = ProjectTask.objects.filter(
                    ProjectId=row['ProjectId'])
                for pro in projectTask:
                    pro.CompanyId = company_id
                    pro.ClientId = client_id
                    pro.save()

            return JsonResponse("updated", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


@csrf_exempt
@api_view(['GET'])
def ProjectTaskTimingCalculation(request):
    # TaskTiming = ProjectTaskTiming.objects.get(ProjectTaskTimingId=ProjectTaskTimingId)
    projectTaskTiming = ProjectTaskTiming.objects.filter(
        Q(Duration__isnull=True) | Q(Duration=""))
    projectTaskTimingSerializer = ProjectTaskTimingSerializer(
        projectTaskTiming, many=True)
    total_duration_minutes = 0
    for row in projectTaskTiming:
        date_format = '%Y-%m-%dT%H:%M:%S%z'
        start_date = datetime.strptime(row.StartDate, date_format)
        end_date = datetime.strptime(row.EndDate, date_format)

        total_time_taken = end_date - start_date
        total_time_taken_in_seconds = total_time_taken.total_seconds()
        total_time_taken_data = {
            'hours': round(total_time_taken_in_seconds // 3600),
            'minutes': round((total_time_taken_in_seconds % 3600) // 60)
        }
        duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
        row.Duration = duration
        row.save()
    return JsonResponse("updated", safe=False)

    #     hours, minutes = map(int, duration.split(':'))
    #     total_duration_minutes += hours * 60 + minutes

    # total_duration_hours = total_duration_minutes // 60
    # total_duration_remaining_minutes = total_duration_minutes % 60
    # total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

    # projectTask = ProjectTask.objects.get(ProjectTaskId=ProjectTaskId)
    # projectTask.TotalDuration = total_duration
    # projectTask.save()


@csrf_exempt
@api_view(['GET'])
def ProjectTaskendatedurationCalculation(request):
    projectTasks = ProjectTask.objects.filter(
        Q(TotalDuration__isnull=True) | Q(TotalDuration="")).exclude(TaskType='Subtask')
    projectTaskSerializer = ProjectTaskSerializer(projectTasks, many=True)
    for row in projectTasks:
        projectTaskTiming = ProjectTaskTiming.objects.filter(
            ProjectTaskId=row.ProjectTaskId).order_by('-SortId')
        projectTaskTimingSerializer = ProjectTaskTimingSerializer(
            projectTaskTiming, many=True)
        if not projectTaskTiming.exists():
            continue
        total_duration_minutes = 0
        for row in projectTaskTiming:
            date_format = '%Y-%m-%dT%H:%M:%S%z'
            start_date = datetime.strptime(row.StartDate, date_format)
            end_date = datetime.strptime(row.EndDate, date_format)

            total_time_taken = end_date - start_date
            total_time_taken_in_seconds = total_time_taken.total_seconds()
            total_time_taken_data = {
                'hours': round(total_time_taken_in_seconds // 3600),
                'minutes': round((total_time_taken_in_seconds % 3600) // 60)
            }
            duration = f"{total_time_taken_data['hours']}:{total_time_taken_data['minutes']}"
            row.Duration = duration
            row.save()

            hours, minutes = map(int, duration.split(':'))
            total_duration_minutes += hours * 60 + minutes

        total_duration_hours = total_duration_minutes // 60
        total_duration_remaining_minutes = total_duration_minutes % 60
        total_duration = f"{total_duration_hours}:{total_duration_remaining_minutes}"

        projectTask = ProjectTask.objects.get(ProjectTaskId=row.ProjectTaskId)

        projectTask.EndDate = projectTaskTimingSerializer.data[0]['EndDate']
        projectTask.TotalDuration = total_duration
        projectTask.save()
    return JsonResponse("updated", safe=False)


@csrf_exempt
@swagger_auto_schema(method='POST', request_body=ProjectDocumentSerializer, operation_description="NOTE: API for save ProjectDocument")
@swagger_auto_schema(method='PUT', request_body=ProjectDocumentSerializer, operation_description="NOTE: API for edit ProjectDocument")
@api_view(['POST', 'PUT'])
@retry(retries=3, delay=2)
def ProjectDocumentApi(request):
    try:
        if request.method == 'POST':
            projectDocumentsData = JSONParser().parse(request)
            projectDocumentsSerializer = ProjectDocumentSerializer(
                data=projectDocumentsData)
            if projectDocumentsSerializer.is_valid():
                projectDocumentsSerializer.save()
                return JsonResponse(projectDocumentsSerializer.data['ProjectDocumentId'], safe=False)
            return JsonResponse("Failed to add", safe=False)
        elif request.method == 'PUT':
            projectDocumentsData = JSONParser().parse(request)
            projectDocuments = ProjectDocument.objects.get(
                ProjectDocumentId=projectDocumentsData['ProjectDocumentId'])
            projectDocumentsSerializer = ProjectDocumentSerializer(
                projectDocuments, data=projectDocumentsData)
            if projectDocumentsSerializer.is_valid():
                projectDocumentsSerializer.save()
                return JsonResponse(projectDocumentsSerializer.data['ProjectDocumentId'], safe=False)
            return JsonResponse("Failed to Update", safe=False)
        else:
            return JsonResponse("", safe=False)
    except:
        return JsonResponse("", safe=False)


class UploadProjectDocument(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        try:
            doc_id = request.data.get('ProjectDocumentId')
            if doc_id:
                try:
                    existing_doc = ProjectDocument.objects.get(ProjectDocumentId=doc_id)
                    serializer = ProjectDocumentSerializer(existing_doc, data=request.data, partial=True)
                    if serializer.is_valid():
                        serializer.save()
                        return JsonResponse(serializer.data['ProjectDocumentId'], safe=False)
                except ProjectDocument.DoesNotExist:
                    pass

            serializer = ProjectDocumentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(serializer.data['ProjectDocumentId'], safe=False)
            else:
                return JsonResponse(serializer.errors, status=400, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500, safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectDocument by ProjectDocumentId")
@swagger_auto_schema(method='DELETE', operation_description="NOTE: API for delete ProjectDocument by ProjectDocumentId")
@api_view(['GET', 'DELETE'])
@retry(retries=3, delay=2)
def ProjectDocumentApiById(request, ProjectDocumentId=""):
    try:
        if request.method == 'GET':
            projectDocument = ProjectDocument.objects.get(
                ProjectDocumentId=ProjectDocumentId)
            projectDocumentSerializer = ProjectDocumentSerializer(projectDocument)
            return JsonResponse(projectDocumentSerializer.data, safe=False)
        elif request.method == 'DELETE':
            projectDocument = ProjectDocument.objects.get(
                ProjectDocumentId=ProjectDocumentId)
            if projectDocument.Document:
                projectDocument.Document.delete(save=False)
            projectDocument.delete()
            return JsonResponse("Deleted successfully", safe=False)
        else:
            return JsonResponse("", safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API for get ProjectDocuments by ProjectId")
@api_view(['GET'])
@retry(retries=3, delay=2)
def ProjectDocumentsByProjectId(request, ProjectId=""):
    try:
        if request.method == 'GET':
            docs = ProjectDocument.objects.filter(ProjectId=ProjectId).order_by('-SortId')
            serializer = ProjectDocumentSerializer(docs, many=True)
            return JsonResponse(serializer.data, safe=False)
        else:
            return JsonResponse([], safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)


# ==========================================================
# ANNUAL MAINTENANCE CONTRACT (AMC) / SERVICE AGREEMENT
# ==========================================================

def _get_ordinal_day(day_num):
    if 11 <= day_num <= 13:
        return f"{day_num}th"
    last_digit = day_num % 10
    if last_digit == 1:
        return f"{day_num}st"
    elif last_digit == 2:
        return f"{day_num}nd"
    elif last_digit == 3:
        return f"{day_num}rd"
    else:
        return f"{day_num}th"


def _format_clause_content(content):
    if not content:
        return ''
    content = str(content).strip()
    if '<' in content and '>' in content:
        return content
    lines = [l.strip() for l in content.split('\n') if l.strip()]
    html_parts = []
    in_list = False
    for line in lines:
        if line.startswith(('-', '*', '•', '●')):
            if not in_list:
                html_parts.append('<ul>')
                in_list = True
            clean_l = line.lstrip('-*•● ').strip()
            if ':' in clean_l and not clean_l.startswith('http'):
                parts = clean_l.split(':', 1)
                clean_l = f'<b>{parts[0].strip()}:</b> {parts[1].strip()}'
            html_parts.append(f'<li>{clean_l}</li>')
        else:
            if in_list:
                html_parts.append('</ul>')
                in_list = False
            html_parts.append(f'<p>{line}</p>')
    if in_list:
        html_parts.append('</ul>')
    return '\n'.join(html_parts)


def build_service_agreement_context(data):
    project_id = data.get('project_id') or data.get('ProjectId')
    project = None
    client = None
    contact_person = None
    client_address_obj = None

    if project_id:
        try:
            project = Project.objects.filter(ProjectId=project_id).first()
            if project and project.ClientId:
                client = Client.objects.filter(ClientId=project.ClientId).first()
                contact_person = ContactPerson.objects.filter(ClientId=project.ClientId).first()
                client_address_obj = (
                    ClientAddress.objects.filter(ClientId=project.ClientId, IsDefaultAddress=True).first()
                    or ClientAddress.objects.filter(ClientId=project.ClientId).first()
                )
        except Exception:
            pass

    # Dates
    effective_date_raw = data.get('effective_date') or datetime.now().strftime('%Y-%m-%d')
    try:
        if isinstance(effective_date_raw, str) and len(effective_date_raw) >= 10:
            effective_date_obj = datetime.strptime(effective_date_raw[:10], '%Y-%m-%d')
        else:
            effective_date_obj = datetime.now()
    except Exception:
        effective_date_obj = datetime.now()

    try:
        duration_years = int(data.get('duration_years', 5) or 5)
    except Exception:
        duration_years = 5

    end_date_obj = effective_date_obj + relativedelta(years=duration_years) - timedelta(days=1)

    effective_date_formatted = f"{_get_ordinal_day(effective_date_obj.day)} day of {effective_date_obj.strftime('%B %Y')}"
    start_date_formatted = effective_date_obj.strftime('%B %d, %Y')
    end_date_formatted = end_date_obj.strftime('%B %d, %Y')
    execution_date = effective_date_obj.strftime('%d-%m-%Y')
    duration_text = f"{duration_years} years"

    # Domain / Platform
    domain_name = data.get('domain_name')
    if not domain_name and project:
        domain_name = project.ProjectName or ""
        domain_name = re.sub(r'^https?:\/\/', '', domain_name).rstrip('/')
    if not domain_name:
        domain_name = "spogprint.com"

    # Client
    client_name = data.get('client_name')
    if not client_name and client:
        client_name = (
            client.CustomerDisplayName
            or client.CompanyName
            or f"{client.FirstName or ''} {client.LastName or ''}".strip()
        )
    if not client_name:
        client_name = "SILVER POINT THE PRINT HOUSE"

    client_address = data.get('client_address')
    if not client_address:
        if client_address_obj:
            addr_parts = [
                client_address_obj.Address1,
                client_address_obj.Address2,
                client_address_obj.City,
                client_address_obj.State,
                client_address_obj.Country,
                client_address_obj.ZipCode
            ]
            client_address = ", ".join([p for p in addr_parts if p])
        elif project and project.Address:
            client_address = project.Address
    if not client_address:
        client_address = "Shed No:05 Caterpillar Building, Salah Al Din St, Al Khabaisi, Deira, United Arab Emirates"

    # Client Signatory
    client_signatory_name = data.get('client_signatory_name')
    if not client_signatory_name and contact_person:
        client_signatory_name = f"{contact_person.FirstName or ''} {contact_person.LastName or ''}".strip()
    if not client_signatory_name:
        client_signatory_name = "KRISHNADAS KAMALON"

    client_signatory_designation = data.get('client_signatory_designation')
    if not client_signatory_designation and contact_person:
        client_signatory_designation = contact_person.Designation or ""
    if not client_signatory_designation:
        client_signatory_designation = "Operations Manager"

    # Service Provider
    service_provider_name = data.get('service_provider_name') or "Cubexizsoft Technologies PVT. LTD."
    service_provider_address = data.get('service_provider_address') or (
        "No. 6/858-M, 2nd Floor, Suite No. 422 Valamkottil Towers, Judgemukku, Kakkanad, Kochi - 682021, Kerala, India"
    )
    service_provider_cin = data.get('service_provider_cin') or "U72900KL2018PTC055399"
    service_provider_gstin = data.get('service_provider_gstin') or "32AAHCC8464C1ZU"
    service_provider_signatory_name = data.get('service_provider_signatory_name') or "MINTO THOMAS"
    service_provider_signatory_designation = data.get('service_provider_signatory_designation') or "Managing Director"

    # Financials
    payment_frequency = data.get('payment_frequency') or "Monthly"
    payment_frequency_title = payment_frequency.capitalize()
    payment_frequency_lower = payment_frequency.lower()
    if 'year' in payment_frequency_lower or 'annual' in payment_frequency_lower:
        payment_period_unit = "year"
    elif 'quarter' in payment_frequency_lower:
        payment_period_unit = "quarter"
    else:
        payment_period_unit = "month"

    currency = data.get('currency') or "AED"
    raw_amount = str(data.get('amount') or "2,000/-").strip()
    if not raw_amount.endswith('/-') and not raw_amount.endswith('.'):
        amount_formatted = f"{raw_amount}/-"
    else:
        amount_formatted = raw_amount

    # Governing Law
    governing_law_country = data.get('governing_law_country') or "the United Arab Emirates (UAE)"

    # Clauses (HTML or formatted text)
    scope_of_services_html = _format_clause_content(data.get('scope_of_services')) if data.get('scope_of_services') else None
    fees_payment_html = _format_clause_content(data.get('fees_payment_terms')) if data.get('fees_payment_terms') else None
    sla_response_html = _format_clause_content(data.get('sla_response_time')) if data.get('sla_response_time') else None
    exclusions_html = _format_clause_content(data.get('exclusions')) if data.get('exclusions') else None
    confidentiality_html = _format_clause_content(data.get('confidentiality_ip')) if data.get('confidentiality_ip') else None
    term_termination_html = _format_clause_content(data.get('term_termination')) if data.get('term_termination') else None
    governing_law_p1_html = _format_clause_content(data.get('governing_law_p1')) if data.get('governing_law_p1') else None
    governing_law_p2_html = _format_clause_content(data.get('governing_law_p2')) if data.get('governing_law_p2') else None

    # Assets
    header_image = os.path.join(settings.BASE_DIR, 'static', 'images', 'amc_header.png')
    footer_image = os.path.join(settings.BASE_DIR, 'static', 'images', 'amc_footer.png')
    seal_image = os.path.join(settings.BASE_DIR, 'static', 'images', 'amc_company_seal.png')
    signature_image = os.path.join(settings.BASE_DIR, 'static', 'images', 'applicant_signature.png')

    return {
        'header_image': header_image if os.path.exists(header_image) else "",
        'footer_image': footer_image if os.path.exists(footer_image) else "",
        'seal_image': seal_image if os.path.exists(seal_image) else "",
        'signature_image': signature_image if os.path.exists(signature_image) else "",
        'domain_name': domain_name,
        'effective_date_formatted': effective_date_formatted,
        'effective_date_obj': effective_date_obj,
        'end_date_obj': end_date_obj,
        'service_provider_name': service_provider_name,
        'service_provider_address': service_provider_address,
        'service_provider_cin': service_provider_cin,
        'service_provider_gstin': service_provider_gstin,
        'client_name': client_name,
        'client_address': client_address,
        'payment_frequency_title': payment_frequency_title,
        'payment_frequency_lower': payment_frequency_lower,
        'currency': currency,
        'amount_formatted': amount_formatted,
        'payment_period_unit': payment_period_unit,
        'duration_text': duration_text,
        'duration_years': duration_years,
        'start_date_formatted': start_date_formatted,
        'end_date_formatted': end_date_formatted,
        'governing_law_country': governing_law_country,
        'service_provider_signatory_name': service_provider_signatory_name,
        'service_provider_signatory_designation': service_provider_signatory_designation,
        'client_signatory_name': client_signatory_name,
        'client_signatory_designation': client_signatory_designation,
        'execution_date': execution_date,
        'scope_of_services_html': scope_of_services_html,
        'fees_payment_html': fees_payment_html,
        'sla_response_html': sla_response_html,
        'exclusions_html': exclusions_html,
        'confidentiality_html': confidentiality_html,
        'term_termination_html': term_termination_html,
        'governing_law_p1_html': governing_law_p1_html,
        'governing_law_p2_html': governing_law_p2_html,
    }


def _render_amc_pdf(context):
    template = get_template('amc_service_agreement.html')
    html = template.render(context)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API to get initial pre-filled AMC Service Agreement data for a Project")
@api_view(['GET'])
def GetServiceAgreementInitialData(request):
    try:
        project_id = request.GET.get('ProjectId') or request.GET.get('project_id') or ""
        ctx = build_service_agreement_context({'project_id': project_id})

        default_scope = (
            f"The Service Provider agrees to provide monthly technical maintenance and support services for the Client's website/platform {ctx['domain_name']}. The services include:\n"
            "- Routine Maintenance & Updates: Regular updates to core application framework, dependencies, and plugins to ensure system stability.\n"
            "- Bug Fixes & Technical Support: Troubleshooting and resolving errors, bugs, and technical issues related to the platform functionality.\n"
            "- Server & Hosting Monitoring: Monitoring server performance, uptime, and database management.\n"
            "- Security & Backups: Regular database and file backups, security updates, and vulnerability patches.\n"
            "- Content / Minor UI Updates: Minor updates to text, images, or configuration settings as requested by the Client."
        )

        default_fees = (
            f"- {ctx['payment_frequency_title']} AMC Fee: The Client agrees to pay the Service Provider a {ctx['payment_frequency_lower']} retainer fee of {ctx['currency']} {ctx['amount_formatted']} per {ctx['payment_period_unit']}.\n"
            f"- Payment Schedule: Payments shall be made in advance/on a {ctx['payment_frequency_lower']} basis on or before the agreed date of each calendar month.\n"
            "- Payment Mode: Payment shall be remitted directly to the Service Provider's designated bank account via Direct Wire Transfer / Bank Transfer."
        )

        default_sla = (
            "- Support Hours: Standard support hours are Monday to Friday.\n"
            "- Critical Issues (Downtime/Major Bug): Response within 2–4 hours.\n"
            "- Non-Critical Updates/Fixes: Response within 24–48 hours."
        )

        default_exclusions = (
            "The following services are not included under this routine AMC agreement and will be charged separately upon mutual agreement:\n"
            "- Major feature additions or complete redesign/re-architecture of the system.\n"
            "- Third-party software/API costs, domain renewal, third-party hosting fees, or external plugin costs.\n"
            "- Issues caused by unauthorized third-party modifications to the source code."
        )

        default_confidentiality = (
            "- Both parties agree to keep all proprietary data, trade secrets, user information, and technical details confidential.\n"
            f"- All custom code developed specifically for {ctx['domain_name']} shall remain/become the property of the Client upon full settlement of dues."
        )

        default_term = (
            f"- Duration: This Agreement is valid for a period of {ctx['duration_text']} starting from {ctx['start_date_formatted']} to {ctx['end_date_formatted']}.\n"
            "- Termination for Convenience: Either party may terminate this Agreement by giving a 30 days' written notice to the other party.\n"
            "- Immediate Termination: Either party may terminate immediately if there is a material breach of terms or non-payment of agreed fees."
        )

        default_governing_p1 = (
            f"This Agreement shall be governed by and construed in accordance with the laws of {ctx['governing_law_country']} for services delivered to the Client's operating entity, and the laws of India for technical development and operational activities conducted by the Service Provider. Any dispute,"
        )

        default_governing_p2 = (
            "controversy, or claim arising out of or relating to this Agreement shall first be attempted to be resolved amicably through good-faith mutual negotiations. If unresolved through negotiation within 30 days, the parties agree that disputes may be referred to international arbitration or subject to the jurisdiction of the courts agreed upon by both parties."
        )

        return JsonResponse({
            'project_id': project_id,
            'effective_date': ctx['effective_date_obj'].strftime('%Y-%m-%d'),
            'duration_years': ctx['duration_years'],
            'payment_frequency': 'Monthly',
            'currency': ctx['currency'],
            'amount': '2,000/-',
            'domain_name': ctx['domain_name'],
            'client_name': ctx['client_name'],
            'client_address': ctx['client_address'],
            'client_signatory_name': ctx['client_signatory_name'],
            'client_signatory_designation': ctx['client_signatory_designation'],
            'service_provider_name': ctx['service_provider_name'],
            'service_provider_address': ctx['service_provider_address'],
            'service_provider_cin': ctx['service_provider_cin'],
            'service_provider_gstin': ctx['service_provider_gstin'],
            'service_provider_signatory_name': ctx['service_provider_signatory_name'],
            'service_provider_signatory_designation': ctx['service_provider_signatory_designation'],
            'governing_law_country': ctx['governing_law_country'],
            'scope_of_services': default_scope,
            'fees_payment_terms': default_fees,
            'sla_response_time': default_sla,
            'exclusions': default_exclusions,
            'confidentiality_ip': default_confidentiality,
            'term_termination': default_term,
            'governing_law_p1': default_governing_p1,
            'governing_law_p2': default_governing_p2,
        }, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500, safe=False)


@csrf_exempt
@swagger_auto_schema(method='GET', operation_description="NOTE: API to generate and view/download AMC Service Agreement PDF")
@swagger_auto_schema(method='POST', operation_description="NOTE: API to generate AMC Service Agreement PDF with customized clauses")
@api_view(['GET', 'POST'])
def GenerateServiceAgreementPDF(request):
    try:
        if request.method == 'POST':
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8'))
            else:
                data = request.POST.dict()
        else:
            data = request.GET.dict()

        context = build_service_agreement_context(data)
        pdf_bytes = _render_amc_pdf(context)
        if pdf_bytes:
            safe_domain = re.sub(r'[^a-zA-Z0-9_-]', '_', context['domain_name'])
            filename = f"AMC_Service_Agreement_{safe_domain}.pdf"
            response = HttpResponse(pdf_bytes, content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{filename}"'
            return response
        else:
            return JsonResponse({"error": "Failed to generate Service Agreement PDF"}, status=500)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
@swagger_auto_schema(method='POST', operation_description="NOTE: API to generate and attach AMC Service Agreement to Project Documents")
@api_view(['POST'])
def SaveServiceAgreementToProject(request):
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST.dict()

        project_id = data.get('project_id') or data.get('ProjectId')
        if not project_id:
            return JsonResponse({"error": "project_id is required"}, status=400)

        context = build_service_agreement_context(data)
        pdf_bytes = _render_amc_pdf(context)
        if not pdf_bytes:
            return JsonResponse({"error": "Failed to render Service Agreement PDF"}, status=500)

        safe_domain = re.sub(r'[^a-zA-Z0-9_-]', '_', context['domain_name'])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"AMC_Service_Agreement_{safe_domain}_{timestamp}.pdf"

        # Destination in media/projectdocuments/
        docs_dir = os.path.join(settings.MEDIA_ROOT, 'projectdocuments')
        os.makedirs(docs_dir, exist_ok=True)
        file_path = os.path.join(docs_dir, filename)

        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)

        relative_doc_path = f"projectdocuments/{filename}"

        # Create or update ProjectDocument
        doc_number = f"AMC/{context['effective_date_obj'].year}/{safe_domain[:8].upper()}"
        doc = ProjectDocument.objects.create(
            ProjectId=project_id,
            Document=relative_doc_path,
            DocumentName=f"AMC Service Agreement - {context['domain_name']}.pdf",
            DocumentType="Service Agreement",
            DocumentNumber=doc_number,
            IssuedOn=context['effective_date_obj'].strftime('%Y-%m-%d'),
            ExpiryDate=context['end_date_obj'].strftime('%Y-%m-%d'),
            Comment=f"Annual Maintenance Contract (AMC) for {context['domain_name']} ({context['currency']} {context['amount_formatted']} / {context['payment_frequency_lower']})"
        )

        return JsonResponse({
            "status": "success",
            "message": "Service Agreement saved to Project Documents successfully",
            "ProjectDocumentId": doc.ProjectDocumentId,
            "DocumentName": doc.DocumentName,
            "DocumentUrl": doc.Document.url if doc.Document else f"/media/{relative_doc_path}",
            "DocumentType": doc.DocumentType,
            "IssuedOn": doc.IssuedOn,
            "ExpiryDate": doc.ExpiryDate
        }, safe=False)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500, safe=False)


